#pragma once

#include <memory>
#include <string>

namespace gamepad_mapper {

class GamepadMapper;

// MCP (Model Control Protocol) Server for dynamic gamepad remapping
// Implements JSON-RPC 2.0 over WebSocket with optional SSL/TLS
class MCPServer {
public:
    explicit MCPServer(std::shared_ptr<GamepadMapper> mapper);
    ~MCPServer();

    // Start server on specified port
    // cert_file/key_file are optional for SSL support
    bool start(unsigned short port,
               const std::string& cert_file = "",
               const std::string& key_file = "");

    // Stop server
    void stop();

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace gamepad_mapper