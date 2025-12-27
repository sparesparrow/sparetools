#pragma once

#include <memory>
#include <string>
#include <vector>
#include <functional>
#include <nlohmann/json.hpp>

namespace gamepad_mapper {

// Forward declaration
struct ControllerInfo;
struct GamepadEvent;

// MCP Prompts Client for connecting to sparesparrow/mcp-prompts server
class MCPPromptsClient {
public:
    // Prompt structure returned by the server
    struct Prompt {
        std::string name;
        std::string description;
        nlohmann::json arguments;
        std::vector<std::string> tags;
    };

    // Context information about user behavior
    struct UserContext {
        std::string application_name;
        std::string window_title;
        std::string current_activity;
        std::vector<std::string> recent_actions;
        std::string user_preferences;
    };

    // Suggested mapping from LLM
    struct MappingSuggestion {
        std::string input_button;
        std::string suggested_output;
        std::string reasoning;
        double confidence_score;
        std::vector<std::string> alternatives;
    };

    explicit MCPPromptsClient(const std::string& server_url = "http://localhost:3000");
    ~MCPPromptsClient();

    // Connection management
    bool connect();
    void disconnect();
    bool is_connected() const;

    // Prompt management
    std::vector<Prompt> list_prompts();
    nlohmann::json get_prompt(const std::string& prompt_name,
                             const nlohmann::json& arguments = {});

    // Context-aware mapping suggestions
    std::vector<MappingSuggestion> get_mapping_suggestions(
        const UserContext& context,
        const std::vector<ControllerInfo>& controllers,
        const std::vector<GamepadEvent>& recent_events
    );

    // Learning and adaptation
    bool send_user_feedback(const std::string& mapping_input,
                           const std::string& mapping_output,
                           bool accepted,
                           const std::string& feedback_reason = "");

    // Dynamic remapping based on context
    std::vector<std::pair<std::string, std::string>> get_dynamic_mappings(
        const UserContext& context
    );

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace gamepad_mapper