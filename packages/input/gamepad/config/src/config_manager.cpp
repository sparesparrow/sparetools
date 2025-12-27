#include "config_manager.h"
#include <fstream>
#include <iostream>
#include <sstream>
#include <algorithm>

namespace gamepad_config {

ConfigManager::ConfigManager() {
    // Set default schema
    schema_ = DEFAULT_CONFIG_SCHEMA;
}

ConfigManager::~ConfigManager() = default;

bool ConfigManager::load_config(const std::string& config_path) {
    try {
        std::ifstream file(config_path);
        if (!file.is_open()) {
            set_error("Failed to open config file: " + config_path);
            return false;
        }

        nlohmann::json loaded_config;
        file >> loaded_config;

        if (!validate_config(loaded_config)) {
            set_error("Configuration validation failed");
            return false;
        }

        config_ = loaded_config;
        return true;
    } catch (const std::exception& e) {
        set_error("Failed to load config: " + std::string(e.what()));
        return false;
    }
}

bool ConfigManager::load_config_from_string(const std::string& config_json) {
    try {
        nlohmann::json loaded_config = nlohmann::json::parse(config_json);

        if (!validate_config(loaded_config)) {
            set_error("Configuration validation failed");
            return false;
        }

        config_ = loaded_config;
        return true;
    } catch (const std::exception& e) {
        set_error("Failed to parse config JSON: " + std::string(e.what()));
        return false;
    }
}

bool ConfigManager::save_config(const std::string& config_path) {
    try {
        std::ofstream file(config_path);
        if (!file.is_open()) {
            set_error("Failed to open config file for writing: " + config_path);
            return false;
        }

        file << config_.dump(2);
        return true;
    } catch (const std::exception& e) {
        set_error("Failed to save config: " + std::string(e.what()));
        return false;
    }
}

void ConfigManager::clear_config() {
    config_ = nlohmann::json::object();
    validation_errors_.clear();
    last_error_.clear();
}

nlohmann::json ConfigManager::get_config() const {
    return config_;
}

bool ConfigManager::set_config(const nlohmann::json& config) {
    if (!validate_config(config)) {
        set_error("Configuration validation failed");
        return false;
    }

    config_ = config;
    return true;
}

bool ConfigManager::update_config(const std::string& key_path, const nlohmann::json& value) {
    return set_nested_value(config_, key_path, value);
}

nlohmann::json ConfigManager::get_value(const std::string& key_path) const {
    return get_nested_value(config_, key_path);
}

bool ConfigManager::validate_config() const {
    return validate_config(config_);
}

bool ConfigManager::validate_config(const nlohmann::json& config) const {
    validation_errors_.clear();

    if (!config.is_object()) {
        validation_errors_.push_back({"root", "Configuration must be a JSON object", config.dump()});
        return false;
    }

    return validate_config_structure(config);
}

std::vector<ValidationError> ConfigManager::get_validation_errors() const {
    return validation_errors_;
}

void ConfigManager::set_schema(const nlohmann::json& schema) {
    schema_ = schema;
}

nlohmann::json ConfigManager::get_schema() const {
    return schema_;
}

bool ConfigManager::validate_against_schema(const nlohmann::json& config) const {
    // Basic schema validation - in a real implementation, you'd use a proper JSON schema validator
    // For now, we'll do basic structural validation

    if (!config.contains("mappings") || !config["mappings"].is_object()) {
        validation_errors_.push_back({"mappings", "Mappings section is required and must be an object", ""});
        return false;
    }

    return true;
}

bool ConfigManager::has_section(const std::string& section_name) const {
    return config_.contains(section_name) && config_[section_name].is_object();
}

nlohmann::json ConfigManager::get_section(const std::string& section_name) const {
    if (has_section(section_name)) {
        return config_[section_name];
    }
    return nlohmann::json();
}

bool ConfigManager::set_section(const std::string& section_name, const nlohmann::json& section) {
    if (!section.is_object()) {
        set_error("Section must be a JSON object");
        return false;
    }

    config_[section_name] = section;
    return true;
}

bool ConfigManager::import_config(const std::string& import_path) {
    nlohmann::json imported_config;
    try {
        std::ifstream file(import_path);
        if (!file.is_open()) {
            set_error("Failed to open import file: " + import_path);
            return false;
        }
        file >> imported_config;
    } catch (const std::exception& e) {
        set_error("Failed to import config: " + std::string(e.what()));
        return false;
    }

    return merge_config(imported_config);
}

bool ConfigManager::export_config(const std::string& export_path, const std::string& format) {
    if (format != "json") {
        set_error("Only JSON format is currently supported");
        return false;
    }

    return save_config(export_path);
}

bool ConfigManager::merge_config(const nlohmann::json& other_config) {
    if (!other_config.is_object()) {
        set_error("Configuration to merge must be a JSON object");
        return false;
    }

    // Deep merge the configurations
    for (auto& [key, value] : other_config.items()) {
        config_[key] = value;
    }

    // Validate the merged configuration
    if (!validate_config()) {
        set_error("Merged configuration validation failed");
        return false;
    }

    return true;
}

std::string ConfigManager::get_last_error() const {
    return last_error_;
}

void ConfigManager::set_error(const std::string& error) {
    last_error_ = error;
    std::cerr << "ConfigManager Error: " << error << std::endl;
}

bool ConfigManager::validate_config_structure(const nlohmann::json& config) const {
    bool is_valid = true;

    // Validate mappings section
    if (config.contains("mappings")) {
        const auto& mappings = config["mappings"];
        if (!mappings.is_object()) {
            validation_errors_.push_back({"mappings", "Mappings must be an object", mappings.dump()});
            is_valid = false;
        } else {
            // Validate each mapping
            for (const auto& [button, mapping] : mappings.items()) {
                if (!mapping.is_object()) {
                    validation_errors_.push_back({button, "Mapping must be an object", mapping.dump()});
                    is_valid = false;
                    continue;
                }

                if (!mapping.contains("type")) {
                    validation_errors_.push_back({button, "Mapping must contain 'type' field", mapping.dump()});
                    is_valid = false;
                    continue;
                }

                std::string type = mapping["type"];
                if (type != "keyboard" && type != "mouse_button" && type != "mouse_scroll" && type != "none") {
                    validation_errors_.push_back({button + ".type", "Invalid mapping type", type});
                    is_valid = false;
                }
            }
        }
    }

    // Validate sensitivity section
    if (config.contains("sensitivity")) {
        const auto& sensitivity = config["sensitivity"];
        if (!sensitivity.is_object()) {
            validation_errors_.push_back({"sensitivity", "Sensitivity must be an object", sensitivity.dump()});
            is_valid = false;
        }
    }

    // Validate audio section
    if (config.contains("audio")) {
        const auto& audio = config["audio"];
        if (!audio.is_object()) {
            validation_errors_.push_back({"audio", "Audio must be an object", audio.dump()});
            is_valid = false;
        }
    }

    return is_valid;
}

nlohmann::json ConfigManager::get_nested_value(const nlohmann::json& obj, const std::string& path) const {
    std::stringstream ss(path);
    std::string token;
    nlohmann::json current = obj;

    while (std::getline(ss, token, '.')) {
        if (!current.contains(token)) {
            return nlohmann::json();
        }
        current = current[token];
    }

    return current;
}

bool ConfigManager::set_nested_value(nlohmann::json& obj, const std::string& path, const nlohmann::json& value) {
    std::stringstream ss(path);
    std::string token;
    nlohmann::json* current = &obj;

    std::vector<std::string> path_parts;
    while (std::getline(ss, token, '.')) {
        path_parts.push_back(token);
    }

    // Navigate to the parent of the target value
    for (size_t i = 0; i < path_parts.size() - 1; ++i) {
        const std::string& part = path_parts[i];
        if (!current->contains(part) || !(*current)[part].is_object()) {
            (*current)[part] = nlohmann::json::object();
        }
        current = &(*current)[part];
    }

    // Set the value
    const std::string& last_part = path_parts.back();
    (*current)[last_part] = value;

    return true;
}

} // namespace gamepad_config