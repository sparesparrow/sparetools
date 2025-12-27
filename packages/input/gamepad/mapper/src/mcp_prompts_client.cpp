#include "mcp_prompts_client.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include "../include/gamepad_events.h"
#include "../include/controller_manager.h"

namespace gamepad_mapper {

class MCPPromptsClient::Impl {
public:
    Impl(const std::string& server_url)
        : server_url_(server_url), connected_(false), curl_(nullptr) {
        curl_global_init(CURL_GLOBAL_DEFAULT);
    }

    ~Impl() {
        disconnect();
        curl_global_cleanup();
    }

    bool connect() {
        if (connected_) return true;

        // Initialize CURL
        curl_ = curl_easy_init();
        if (!curl_) {
            std::cerr << "Failed to initialize CURL" << std::endl;
            return false;
        }

        // Test connection by making a simple request
        nlohmann::json test_request = {
            {"jsonrpc", "2.0"},
            {"id", 1},
            {"method", "initialize"},
            {"params", {
                {"protocolVersion", "2024-11-05"},
                {"capabilities", {}},
                {"clientInfo", {
                    {"name", "gamepad-mapper"},
                    {"version", "1.0.0"}
                }}
            }}
        };

        auto response = make_request(test_request);
        if (!response || response->contains("error")) {
            std::cerr << "Failed to connect to MCP prompts server" << std::endl;
            curl_easy_cleanup(curl_);
            curl_ = nullptr;
            return false;
        }

        connected_ = true;
        std::cout << "Connected to MCP prompts server at " << server_url_ << std::endl;
        return true;
    }

    void disconnect() {
        if (curl_) {
            curl_easy_cleanup(curl_);
            curl_ = nullptr;
        }
        connected_ = false;
    }

    bool is_connected() const {
        return connected_;
    }

    std::vector<MCPPromptsClient::Prompt> list_prompts() {
        if (!connected_) return {};

        nlohmann::json request = {
            {"jsonrpc", "2.0"},
            {"id", 2},
            {"method", "prompts/list"},
            {"params", {}}
        };

        auto response = make_request(request);
        if (!response || !response->contains("result")) {
            return {};
        }

        std::vector<MCPPromptsClient::Prompt> prompts;
        if (response->contains("result") && response->at("result").contains("prompts")) {
            for (const auto& prompt_json : response->at("result").at("prompts")) {
                MCPPromptsClient::Prompt prompt;
                prompt.name = prompt_json.value("name", "");
                prompt.description = prompt_json.value("description", "");

                if (prompt_json.contains("arguments")) {
                    prompt.arguments = prompt_json.at("arguments");
                }

                if (prompt_json.contains("tags")) {
                    for (const auto& tag : prompt_json.at("tags")) {
                        prompt.tags.push_back(tag);
                    }
                }

                prompts.push_back(prompt);
            }
        }

        return prompts;
    }

    nlohmann::json get_prompt(const std::string& prompt_name, const nlohmann::json& arguments) {
        if (!connected_) return {};

        nlohmann::json request = {
            {"jsonrpc", "2.0"},
            {"id", 3},
            {"method", "prompts/get"},
            {"params", {
                {"name", prompt_name},
                {"arguments", arguments}
            }}
        };

        auto response = make_request(request);
        if (!response || !response->contains("result")) {
            return {};
        }

        return response->at("result");
    }

    std::vector<MCPPromptsClient::MappingSuggestion> get_mapping_suggestions(
        const MCPPromptsClient::UserContext& context,
        const std::vector<ControllerInfo>& controllers,
        const std::vector<GamepadEvent>& recent_events
    ) {
        if (!connected_) return {};

        // Convert context to JSON
        nlohmann::json context_json = {
            {"application_name", context.application_name},
            {"window_title", context.window_title},
            {"current_activity", context.current_activity},
            {"recent_actions", context.recent_actions},
            {"user_preferences", context.user_preferences}
        };

        // Convert controllers to JSON
        nlohmann::json controllers_json = nlohmann::json::array();
        for (const auto& controller : controllers) {
            controllers_json.push_back({
                {"id", controller.id},
                {"name", controller.name},
                {"type", controller.type},
                {"connected", controller.connected}
            });
        }

        // Convert recent events to JSON
        nlohmann::json events_json = nlohmann::json::array();
        for (const auto& event : recent_events) {
            events_json.push_back({
                {"type", static_cast<int>(event.type)},
                {"button", event.button},
                {"axis", event.axis},
                {"value", event.value},
                {"timestamp", event.timestamp}
            });
        }

        nlohmann::json request = {
            {"jsonrpc", "2.0"},
            {"id", 4},
            {"method", "gamepad/get_mapping_suggestions"},
            {"params", {
                {"context", context_json},
                {"controllers", controllers_json},
                {"recent_events", events_json}
            }}
        };

        auto response = make_request(request);
        if (!response || !response->contains("result") ||
            !response->at("result").contains("suggestions")) {
            return {};
        }

        std::vector<MCPPromptsClient::MappingSuggestion> suggestions;
        for (const auto& suggestion_json : response->at("result").at("suggestions")) {
            MCPPromptsClient::MappingSuggestion suggestion;
            suggestion.input_button = suggestion_json.value("input_button", "");
            suggestion.suggested_output = suggestion_json.value("suggested_output", "");
            suggestion.reasoning = suggestion_json.value("reasoning", "");
            suggestion.confidence_score = suggestion_json.value("confidence_score", 0.0);

            if (suggestion_json.contains("alternatives")) {
                for (const auto& alt : suggestion_json.at("alternatives")) {
                    suggestion.alternatives.push_back(alt);
                }
            }

            suggestions.push_back(suggestion);
        }

        return suggestions;
    }

    bool send_user_feedback(const std::string& mapping_input,
                           const std::string& mapping_output,
                           bool accepted,
                           const std::string& feedback_reason) {
        if (!connected_) return false;

        nlohmann::json request = {
            {"jsonrpc", "2.0"},
            {"id", 5},
            {"method", "gamepad/send_feedback"},
            {"params", {
                {"mapping_input", mapping_input},
                {"mapping_output", mapping_output},
                {"accepted", accepted},
                {"feedback_reason", feedback_reason}
            }}
        };

        auto response = make_request(request);
        return response && !response->contains("error");
    }

    std::vector<std::pair<std::string, std::string>> get_dynamic_mappings(
        const MCPPromptsClient::UserContext& context
    ) {
        if (!connected_) return {};

        nlohmann::json context_json = {
            {"application_name", context.application_name},
            {"window_title", context.window_title},
            {"current_activity", context.current_activity},
            {"recent_actions", context.recent_actions},
            {"user_preferences", context.user_preferences}
        };

        nlohmann::json request = {
            {"jsonrpc", "2.0"},
            {"id", 6},
            {"method", "gamepad/get_dynamic_mappings"},
            {"params", {
                {"context", context_json}
            }}
        };

        auto response = make_request(request);
        if (!response || !response->contains("result") ||
            !response->at("result").contains("mappings")) {
            return {};
        }

        std::vector<std::pair<std::string, std::string>> mappings;
        for (const auto& mapping_json : response->at("result").at("mappings")) {
            std::string input = mapping_json.value("input", "");
            std::string output = mapping_json.value("output", "");
            if (!input.empty() && !output.empty()) {
                mappings.emplace_back(input, output);
            }
        }

        return mappings;
    }

private:
    static size_t write_callback(void* contents, size_t size, size_t nmemb, std::string* response) {
        size_t total_size = size * nmemb;
        response->append(static_cast<char*>(contents), total_size);
        return total_size;
    }

    std::unique_ptr<nlohmann::json> make_request(const nlohmann::json& request) {
        if (!curl_) return nullptr;

        std::string request_body = request.dump();
        std::string response_body;

        curl_easy_setopt(curl_, CURLOPT_URL, server_url_.c_str());
        curl_easy_setopt(curl_, CURLOPT_POST, 1L);
        curl_easy_setopt(curl_, CURLOPT_POSTFIELDS, request_body.c_str());
        curl_easy_setopt(curl_, CURLOPT_POSTFIELDSIZE, request_body.length());

        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl_, CURLOPT_HTTPHEADER, headers);

        curl_easy_setopt(curl_, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl_, CURLOPT_WRITEDATA, &response_body);

        // Set timeout
        curl_easy_setopt(curl_, CURLOPT_TIMEOUT, 10L);

        CURLcode res = curl_easy_perform(curl_);

        curl_slist_free_all(headers);

        if (res != CURLE_OK) {
            std::cerr << "CURL request failed: " << curl_easy_strerror(res) << std::endl;
            return nullptr;
        }

        try {
            auto response = std::make_unique<nlohmann::json>(nlohmann::json::parse(response_body));
            return response;
        } catch (const std::exception& e) {
            std::cerr << "Failed to parse JSON response: " << e.what() << std::endl;
            return nullptr;
        }
    }

    std::string server_url_;
    bool connected_;
    CURL* curl_;
    int request_id_counter_ = 1;
};

// Public interface implementation
MCPPromptsClient::MCPPromptsClient(const std::string& server_url)
    : impl_(std::make_unique<Impl>(server_url)) {}

MCPPromptsClient::~MCPPromptsClient() = default;

bool MCPPromptsClient::connect() {
    return impl_->connect();
}

void MCPPromptsClient::disconnect() {
    impl_->disconnect();
}

bool MCPPromptsClient::is_connected() const {
    return impl_->is_connected();
}

std::vector<MCPPromptsClient::Prompt> MCPPromptsClient::list_prompts() {
    return impl_->list_prompts();
}

nlohmann::json MCPPromptsClient::get_prompt(const std::string& prompt_name, const nlohmann::json& arguments) {
    return impl_->get_prompt(prompt_name, arguments);
}

std::vector<MCPPromptsClient::MappingSuggestion> MCPPromptsClient::get_mapping_suggestions(
    const MCPPromptsClient::UserContext& context,
    const std::vector<ControllerInfo>& controllers,
    const std::vector<GamepadEvent>& recent_events
) {
    return impl_->get_mapping_suggestions(context, controllers, recent_events);
}

bool MCPPromptsClient::send_user_feedback(const std::string& mapping_input,
                                        const std::string& mapping_output,
                                        bool accepted,
                                        const std::string& feedback_reason) {
    return impl_->send_user_feedback(mapping_input, mapping_output, accepted, feedback_reason);
}

std::vector<std::pair<std::string, std::string>> MCPPromptsClient::get_dynamic_mappings(
    const MCPPromptsClient::UserContext& context
) {
    return impl_->get_dynamic_mappings(context);
}

} // namespace gamepad_mapper