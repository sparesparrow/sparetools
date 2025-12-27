#pragma once

#include "Protocol/Entity/Server.h"
#include <memory>

namespace gamepad_mapper {

class GamepadMapper;

// MCP Server for gamepad mapping operations
class GamepadServer : public MCP::CMCPServer<GamepadServer> {
public:
    static constexpr const char* SERVER_NAME = "gamepad_mapper";
    static constexpr const char* SERVER_VERSION = "1.0.0";

    // Initialize the server with a gamepad mapper instance
    int Initialize(std::shared_ptr<GamepadMapper> mapper);
    
    // Override base class pure virtual method
    int Initialize() override;

    // Get singleton instance
    static GamepadServer& GetInstance() {
        return s_Instance;
    }

private:
    friend class MCP::CMCPServer<GamepadServer>;
    GamepadServer() = default;

    std::shared_ptr<GamepadMapper> mapper_;
    static GamepadServer s_Instance;
};

// Static member definition
GamepadServer GamepadServer::s_Instance;

} // namespace gamepad_mapper