#pragma once

#include <nlohmann/json.hpp>
#include <string>
#include <vector>
#include <memory>

namespace gamepad_config {

/**
 * @brief Validation error information
 */
struct ValidationError {
    std::string field;
    std::string message;
    std::string value;
};

/**
 * @brief Configuration manager for gamepad mappings and settings
 *
 * Provides comprehensive configuration management including loading,
 * saving, validation, and preset management for gamepad mappings.
 */
class ConfigManager {
public:
    /**
     * @brief Constructor
     */
    ConfigManager();

    /**
     * @brief Destructor
     */
    ~ConfigManager();

    /**
     * @brief Load configuration from file
     * @param config_path Path to JSON configuration file
     * @return true if loaded successfully, false otherwise
     */
    bool load_config(const std::string& config_path);

    /**
     * @brief Load configuration from JSON string
     * @param config_json JSON configuration string
     * @return true if loaded successfully, false otherwise
     */
    bool load_config_from_string(const std::string& config_json);

    /**
     * @brief Save configuration to file
     * @param config_path Path to save configuration
     * @return true if saved successfully, false otherwise
     */
    bool save_config(const std::string& config_path);

    /**
     * @brief Clear current configuration
     */
    void clear_config();

    /**
     * @brief Get current configuration
     * @return Current configuration as JSON
     */
    nlohmann::json get_config() const;

    /**
     * @brief Set configuration
     * @param config New configuration
     * @return true if set successfully, false otherwise
     */
    bool set_config(const nlohmann::json& config);

    /**
     * @brief Update configuration value at path
     * @param key_path Dot-separated path (e.g., "mappings.A.type")
     * @param value New value
     * @return true if updated successfully, false otherwise
     */
    bool update_config(const std::string& key_path, const nlohmann::json& value);

    /**
     * @brief Get configuration value at path
     * @param key_path Dot-separated path
     * @return Value at path, or null if not found
     */
    nlohmann::json get_value(const std::string& key_path) const;

    /**
     * @brief Validate current configuration
     * @return true if valid, false otherwise
     */
    bool validate_config() const;

    /**
     * @brief Validate specific configuration
     * @param config Configuration to validate
     * @return true if valid, false otherwise
     */
    bool validate_config(const nlohmann::json& config) const;

    /**
     * @brief Get validation errors
     * @return List of validation errors
     */
    std::vector<ValidationError> get_validation_errors() const;

    /**
     * @brief Set JSON schema for validation
     * @param schema JSON schema
     */
    void set_schema(const nlohmann::json& schema);

    /**
     * @brief Get current validation schema
     * @return Current schema
     */
    nlohmann::json get_schema() const;

    /**
     * @brief Validate against schema
     * @param config Configuration to validate
     * @return true if valid against schema, false otherwise
     */
    bool validate_against_schema(const nlohmann::json& config) const;

    /**
     * @brief Check if section exists
     * @param section_name Section name
     * @return true if section exists, false otherwise
     */
    bool has_section(const std::string& section_name) const;

    /**
     * @brief Get configuration section
     * @param section_name Section name
     * @return Section configuration, or null if not found
     */
    nlohmann::json get_section(const std::string& section_name) const;

    /**
     * @brief Set configuration section
     * @param section_name Section name
     * @param section Section configuration
     * @return true if set successfully, false otherwise
     */
    bool set_section(const std::string& section_name, const nlohmann::json& section);

    /**
     * @brief Import configuration from file
     * @param import_path Path to import from
     * @return true if imported successfully, false otherwise
     */
    bool import_config(const std::string& import_path);

    /**
     * @brief Export configuration to file
     * @param export_path Path to export to
     * @param format Export format (currently only JSON supported)
     * @return true if exported successfully, false otherwise
     */
    bool export_config(const std::string& export_path, const std::string& format = "json");

    /**
     * @brief Merge another configuration
     * @param other_config Configuration to merge
     * @return true if merged successfully, false otherwise
     */
    bool merge_config(const nlohmann::json& other_config);

    /**
     * @brief Get last error message
     * @return Last error message
     */
    std::string get_last_error() const;

private:
    nlohmann::json config_;
    nlohmann::json schema_;
    std::vector<ValidationError> validation_errors_;
    std::string last_error_;

    /**
     * @brief Set last error message
     * @param error Error message
     */
    void set_error(const std::string& error);

    /**
     * @brief Validate configuration structure
     * @param config Configuration to validate
     * @return true if structure is valid, false otherwise
     */
    bool validate_config_structure(const nlohmann::json& config) const;

    /**
     * @brief Get nested value by path
     * @param obj JSON object
     * @param path Dot-separated path
     * @return Value at path, or null if not found
     */
    nlohmann::json get_nested_value(const nlohmann::json& obj, const std::string& path) const;

    /**
     * @brief Set nested value by path
     * @param obj JSON object to modify
     * @param path Dot-separated path
     * @param value Value to set
     * @return true if set successfully, false otherwise
     */
    bool set_nested_value(nlohmann::json& obj, const std::string& path, const nlohmann::json& value);
};

// Default configuration schema
static const nlohmann::json DEFAULT_CONFIG_SCHEMA = {
    {"type", "object"},
    {"properties", {
        {"mappings", {
            {"type", "object"},
            {"description", "Button mapping configuration"},
            {"patternProperties", {
                {".*", {
                    {"type", "object"},
                    {"properties", {
                        {"type", {
                            {"type", "string"},
                            {"enum", {"keyboard", "mouse_button", "mouse_scroll", "none"}}
                        }},
                        {"key", {{"type", "string"}}},
                        {"button", {{"type", "string"}}},
                        {"modifiers", {{"type", "array"}}}
                    }},
                    {"required", {"type"}}
                }}
            }}
        }},
        {"sensitivity", {
            {"type", "object"},
            {"properties", {
                {"stick_deadzone", {{"type", "number"}, {"minimum", 0.0}, {"maximum", 1.0}}},
                {"trigger_threshold", {{"type", "number"}, {"minimum", 0.0}, {"maximum", 1.0}}}
            }}
        }},
        {"audio", {
            {"type", "object"},
            {"properties", {
                {"voice_alerts", {{"type", "boolean"}}},
                {"sound_effects", {{"type", "boolean"}}},
                {"volume", {{"type", "number"}, {"minimum", 0.0}, {"maximum", 1.0}}}
            }}
        }}
    }}
};

} // namespace gamepad_config