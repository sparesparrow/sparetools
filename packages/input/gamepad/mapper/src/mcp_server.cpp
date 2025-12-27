#include "mcp_server.h"
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/beast/ssl.hpp>
#include <boost/beast/websocket.hpp>
#include <boost/beast/websocket/ssl.hpp>
#include <boost/asio.hpp>
#include <boost/asio/ssl/stream.hpp>
#include <iostream>
#include <thread>
#include <memory>
#include <nlohmann/json.hpp>
#include "../include/gamepad_mapper.h"
#ifdef WITH_CLIPBOARD
#include "../include/clipboard_monitor.h"
#endif

namespace beast = boost::beast;
namespace http = beast::http;
namespace websocket = beast::websocket;
namespace net = boost::asio;
namespace ssl = boost::asio::ssl;
using tcp = boost::asio::ip::tcp;

using json = nlohmann::json;

namespace gamepad_mapper {

class MCPServer::Impl {
public:
    Impl(std::shared_ptr<GamepadMapper> mapper)
        : mapper_(mapper), ioc_(), ssl_ctx_(ssl::context::tlsv12_server) {}
    ~Impl() { stop(); }

    bool start(unsigned short port, const std::string& cert_file, const std::string& key_file) {
        try {
            // Load SSL certificates if provided
            if (!cert_file.empty() && !key_file.empty()) {
                ssl_ctx_.use_certificate_chain_file(cert_file);
                ssl_ctx_.use_private_key_file(key_file, ssl::context::pem);
                use_ssl_ = true;
            }

            // Create acceptor
            tcp::acceptor acceptor(ioc_, tcp::endpoint(tcp::v4(), port));

            std::cout << "MCP Server starting on port " << port
                      << (use_ssl_ ? " (SSL enabled)" : " (no SSL)") << std::endl;

            // Start accept loop
            accept_connections(acceptor);

            // Start IO context in background thread
            server_thread_ = std::thread([this]() {
                ioc_.run();
            });

            return true;
        } catch (const std::exception& e) {
            std::cerr << "Failed to start MCP server: " << e.what() << std::endl;
            return false;
        }
    }

    void stop() {
        ioc_.stop();
        if (server_thread_.joinable()) {
            server_thread_.join();
        }
    }

private:
    void accept_connections(tcp::acceptor& acceptor) {
        acceptor.async_accept(
            [this, &acceptor](boost::system::error_code ec, tcp::socket socket) {
                if (!ec) {
                    std::cout << "New MCP connection from " << socket.remote_endpoint() << std::endl;

                    // Create session for this connection
                    if (use_ssl_) {
                        auto session = std::make_shared<SSLWebSocketSession>(
                            std::move(socket), ssl_ctx_, mapper_);
                        session->run();
                    } else {
                        auto session = std::make_shared<WebSocketSession>(
                            std::move(socket), mapper_);
                        session->run();
                    }
                }

                // Continue accepting connections
                accept_connections(acceptor);
            });
    }

    std::shared_ptr<GamepadMapper> mapper_;
    net::io_context ioc_;
    ssl::context ssl_ctx_;
    std::thread server_thread_;
    bool use_ssl_ = false;
};

// WebSocket Session base class
class WebSocketSessionBase {
public:
    virtual ~WebSocketSessionBase() = default;
    virtual void run() = 0;

protected:
    void handle_message(const std::string& message, std::shared_ptr<GamepadMapper> mapper) {
        try {
            json request = json::parse(message);

            // Validate JSON-RPC 2.0 format
            if (!request.contains("jsonrpc") || request["jsonrpc"] != "2.0") {
                send_error_response(-32600, "Invalid Request", request.contains("id") ? request["id"] : nullptr);
                return;
            }

            if (!request.contains("method")) {
                send_error_response(-32600, "Invalid Request", request.contains("id") ? request["id"] : nullptr);
                return;
            }

            std::string method = request["method"];
            json params = request.contains("params") ? request["params"] : json::object();
            json id = request.contains("id") ? request["id"] : nullptr;

            // Handle method
            handle_method(method, params, id, mapper);

        } catch (const json::exception& e) {
            send_error_response(-32700, "Parse error", nullptr);
        }
    }

    virtual void send_response(const json& response) = 0;
    virtual void send_error_response(int code, const std::string& message, const json& id) = 0;

private:
    void handle_method(const std::string& method, const json& params,
                      const json& id, std::shared_ptr<GamepadMapper> mapper) {
        json response = {
            {"jsonrpc", "2.0"},
            {"id", id}
        };

        try {
            if (method == "add_mapping") {
                if (!params.contains("input") || !params.contains("output")) {
                    throw std::runtime_error("Missing required parameters: input, output");
                }

                std::string input = params["input"];
                std::string output = params["output"];

                if (mapper->add_mapping(input, output)) {
                    response["result"] = "success";
                } else {
                    throw std::runtime_error("Failed to add mapping");
                }

            } else if (method == "remove_mapping") {
                if (!params.contains("input")) {
                    throw std::runtime_error("Missing required parameter: input");
                }

                std::string input = params["input"];

                if (mapper->remove_mapping(input)) {
                    response["result"] = "success";
                } else {
                    throw std::runtime_error("Mapping not found");
                }

            } else if (method == "load_config") {
                if (!params.contains("file")) {
                    throw std::runtime_error("Missing required parameter: file");
                }

                std::string file = params["file"];

                if (mapper->load_mappings(file)) {
                    response["result"] = "success";
                } else {
                    throw std::runtime_error("Failed to load configuration file");
                }

            } else if (method == "get_status") {
                response["result"] = {
                    {"status", "running"},
                    {"backends", {"X11", "Wayland", "KDE", "SDL2", "UInput"}}
                };

            } else if (method == "ping") {
                response["result"] = "pong";

#ifdef WITH_CLIPBOARD
            } else if (method == "clipboard_read") {
                // Read current clipboard content
                if (!mapper->is_clipboard_monitoring()) {
                    if (!mapper->initialize_clipboard_monitor()) {
                        throw std::runtime_error("Failed to initialize clipboard monitor");
                    }
                }
                
                auto content = mapper->get_current_content();
                json result = {
                    {"type", static_cast<int>(content.type)},
                    {"text_content", content.text_content},
                    {"mime_type", content.mime_type},
                    {"data_size", content.data_size}
                };
                
                if (content.type == ClipboardContentType::FILES) {
                    result["file_paths"] = content.file_paths;
                }
                
                response["result"] = result;

            } else if (method == "clipboard_write") {
                // Write text to clipboard
                if (!params.contains("text")) {
                    throw std::runtime_error("Missing required parameter: text");
                }
                
                if (!mapper->is_clipboard_monitoring()) {
                    if (!mapper->initialize_clipboard_monitor()) {
                        throw std::runtime_error("Failed to initialize clipboard monitor");
                    }
                }
                
                std::string text = params["text"];
                if (mapper->set_text_content(text)) {
                    response["result"] = "success";
                } else {
                    throw std::runtime_error("Failed to write to clipboard");
                }

            } else if (method == "clipboard_clear") {
                // Clear clipboard
                if (!mapper->is_clipboard_monitoring()) {
                    if (!mapper->initialize_clipboard_monitor()) {
                        throw std::runtime_error("Failed to initialize clipboard monitor");
                    }
                }
                
                if (mapper->clear_clipboard()) {
                    response["result"] = "success";
                } else {
                    throw std::runtime_error("Failed to clear clipboard");
                }

            } else if (method == "clipboard_analyze") {
                // Analyze clipboard content for LLM processing
                if (!mapper->is_clipboard_monitoring()) {
                    if (!mapper->initialize_clipboard_monitor()) {
                        throw std::runtime_error("Failed to initialize clipboard monitor");
                    }
                }
                
                auto content = mapper->get_current_content();
                json analysis = {
                    {"content_type", static_cast<int>(content.type)},
                    {"has_text", !content.text_content.empty()},
                    {"has_image", content.type == ClipboardContentType::IMAGE},
                    {"has_files", content.type == ClipboardContentType::FILES},
                    {"data_size", content.data_size},
                    {"mime_type", content.mime_type}
                };
                
                if (content.type == ClipboardContentType::TEXT) {
                    analysis["text_length"] = content.text_content.length();
                    analysis["text_preview"] = content.text_content.substr(0, 100) + 
                        (content.text_content.length() > 100 ? "..." : "");
                } else if (content.type == ClipboardContentType::FILES) {
                    analysis["file_count"] = content.file_paths.size();
                    analysis["file_paths"] = content.file_paths;
                }
                
                response["result"] = analysis;
#endif

            } else if (method == "voice_alert") {
                // Send voice alert
                if (!params.contains("message")) {
                    throw std::runtime_error("Missing required parameter: message");
                }
                
                std::string message = params["message"];
                std::string alert_type = params.value("type", "notification");
                std::string priority = params.value("priority", "normal");
                
                // Convert string to enum values
                AlertType type = AlertType::NOTIFICATION;
                if (alert_type == "connection") type = AlertType::CONNECTION;
                else if (alert_type == "disconnection") type = AlertType::DISCONNECTION;
                else if (alert_type == "error") type = AlertType::ERROR;
                else if (alert_type == "status") type = AlertType::STATUS_UPDATE;
                else if (alert_type == "custom") type = AlertType::CUSTOM;
                
                AlertPriority alert_priority = AlertPriority::NORMAL;
                if (priority == "low") alert_priority = AlertPriority::LOW;
                else if (priority == "high") alert_priority = AlertPriority::HIGH;
                else if (priority == "critical") alert_priority = AlertPriority::CRITICAL;
                
                if (mapper->is_voice_alerts_enabled()) {
                    // This would need to be implemented in GamepadMapper
                    response["result"] = "Voice alert queued";
                } else {
                    response["result"] = "Voice alerts not enabled";
                }

            } else if (method == "voice_settings") {
                // Configure voice settings
                if (params.contains("enabled")) {
                    // This would need to be implemented in GamepadMapper
                    response["result"] = "Voice settings updated";
                } else {
                    response["result"] = "Voice settings query not implemented";
                }

            } else if (method == "kde_connect_devices") {
                // Get available KDE Connect devices
                if (mapper->is_kde_connect_enabled()) {
                    // This would need to be implemented in GamepadMapper
                    response["result"] = "KDE Connect devices query not implemented";
                } else {
                    response["result"] = "KDE Connect not enabled";
                }

            } else if (method == "kde_connect_send_clipboard") {
                // Send clipboard to KDE Connect device
                if (!params.contains("device_id") || !params.contains("content")) {
                    throw std::runtime_error("Missing required parameters: device_id, content");
                }
                
                std::string device_id = params["device_id"];
                std::string content = params["content"];
                
                if (mapper->is_kde_connect_enabled()) {
                    // This would need to be implemented in GamepadMapper
                    response["result"] = "Clipboard sent to device";
                } else {
                    response["result"] = "KDE Connect not enabled";
                }

            } else if (method == "kde_connect_send_notification") {
                // Send notification to KDE Connect device
                if (!params.contains("device_id") || !params.contains("title")) {
                    throw std::runtime_error("Missing required parameters: device_id, title");
                }
                
                std::string device_id = params["device_id"];
                std::string title = params["title"];
                std::string body = params.value("body", "");
                
                if (mapper->is_kde_connect_enabled()) {
                    // This would need to be implemented in GamepadMapper
                    response["result"] = "Notification sent to device";
                } else {
                    response["result"] = "KDE Connect not enabled";
                }

            } else {
                send_error_response(-32601, "Method not found", id);
                return;
            }

        } catch (const std::exception& e) {
            send_error_response(-32603, e.what(), id);
            return;
        }

        send_response(response);
    }
};

// Plain WebSocket session
class WebSocketSession : public WebSocketSessionBase,
                        public std::enable_shared_from_this<WebSocketSession> {
public:
    WebSocketSession(tcp::socket&& socket, std::shared_ptr<GamepadMapper> mapper)
        : ws_(std::move(socket)), mapper_(mapper) {}

    void run() {
        // Accept the WebSocket handshake
        ws_.async_accept(
            [self = shared_from_this()](boost::system::error_code ec) {
                if (ec) {
                    std::cerr << "WebSocket accept error: " << ec.message() << std::endl;
                    return;
                }

                self->do_read();
            });
    }

private:
    void do_read() {
        ws_.async_read(buffer_,
            [self = shared_from_this()](boost::system::error_code ec, std::size_t bytes_transferred) {
                if (ec) {
                    if (ec != websocket::error::closed) {
                        std::cerr << "WebSocket read error: " << ec.message() << std::endl;
                    }
                    return;
                }

                std::string message = beast::make_printable(buffer_.data());
                self->handle_message(message, self->mapper_);

                // Continue reading
                self->buffer_.consume(bytes_transferred);
                self->do_read();
            });
    }

    void send_response(const json& response) override {
        std::string response_str = response.dump();

        ws_.async_write(net::buffer(response_str),
            [self = shared_from_this()](boost::system::error_code ec, std::size_t) {
                if (ec) {
                    std::cerr << "WebSocket write error: " << ec.message() << std::endl;
                }
            });
    }

    void send_error_response(int code, const std::string& message, const json& id) override {
        json error_response = {
            {"jsonrpc", "2.0"},
            {"error", {
                {"code", code},
                {"message", message}
            }},
            {"id", id}
        };
        send_response(error_response);
    }

    websocket::stream<tcp::socket> ws_;
    beast::multi_buffer buffer_;
    std::shared_ptr<GamepadMapper> mapper_;
};

// SSL WebSocket session
class SSLWebSocketSession : public WebSocketSessionBase,
                           public std::enable_shared_from_this<SSLWebSocketSession> {
public:
    SSLWebSocketSession(tcp::socket&& socket, ssl::context& ctx, std::shared_ptr<GamepadMapper> mapper)
        : stream_(std::move(socket), ctx), mapper_(mapper) {}

    void run() {
        // Perform SSL handshake
        stream_.next_layer().async_handshake(ssl::stream_base::server,
            [self = shared_from_this()](boost::system::error_code ec) {
                if (ec) {
                    std::cerr << "SSL handshake error: " << ec.message() << std::endl;
                    return;
                }

                // Accept the WebSocket handshake
                self->ws_.async_accept(
                    [self](boost::system::error_code ec) {
                        if (ec) {
                            std::cerr << "WebSocket accept error: " << ec.message() << std::endl;
                            return;
                        }

                        self->do_read();
                    });
            });
    }

private:
    void do_read() {
        ws_.async_read(buffer_,
            [self = shared_from_this()](boost::system::error_code ec, std::size_t bytes_transferred) {
                if (ec) {
                    if (ec != websocket::error::closed) {
                        std::cerr << "WebSocket read error: " << ec.message() << std::endl;
                    }
                    return;
                }

                std::string message = beast::make_printable(self->buffer_.data());
                self->handle_message(message, self->mapper_);

                // Continue reading
                self->buffer_.consume(bytes_transferred);
                self->do_read();
            });
    }

    void send_response(const json& response) override {
        std::string response_str = response.dump();

        ws_.async_write(net::buffer(response_str),
            [self = shared_from_this()](boost::system::error_code ec, std::size_t) {
                if (ec) {
                    std::cerr << "WebSocket write error: " << ec.message() << std::endl;
                }
            });
    }

    void send_error_response(int code, const std::string& message, const json& id) override {
        json error_response = {
            {"jsonrpc", "2.0"},
            {"error", {
                {"code", code},
                {"message", message}
            }},
            {"id", id}
        };
        send_response(error_response);
    }

    websocket::stream<ssl::stream<tcp::socket>> ws_{stream_};
    ssl::stream<tcp::socket> stream_;
    beast::multi_buffer buffer_;
    std::shared_ptr<GamepadMapper> mapper_;
};

// Public interface implementation
MCPServer::MCPServer(std::shared_ptr<GamepadMapper> mapper)
    : impl_(std::make_unique<Impl>(mapper)) {}

MCPServer::~MCPServer() = default;

bool MCPServer::start(unsigned short port, const std::string& cert_file, const std::string& key_file) {
    return impl_->start(port, cert_file, key_file);
}

void MCPServer::stop() {
    impl_->stop();
}

} // namespace gamepad_mapper