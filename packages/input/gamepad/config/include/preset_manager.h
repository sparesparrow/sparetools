#pragma once

#include <nlohmann/json.hpp>
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>

namespace gamepad_config {

/**
 * @brief Preset metadata information
 */
struct PresetMetadata {
    std::string name;
    std::string description;
    std::string category;
    std::string author;
    std::string version;
    std::string created_date;
    std::vector<std::string> tags;
};

/**
 * @brief Preset information structure
 */
struct PresetInfo {
    std::string name;
    std::string path;
    PresetMetadata metadata;
    bool is_valid;
};

/**
 * @brief Preset manager for managing configuration presets
 *
 * Provides functionality to load, save, and manage gamepad configuration presets
 * from multiple directories with categorization and validation.
 */
class PresetManager {
public:
    /**
     * @brief Constructor
     */
    PresetManager();

    /**
     * @brief Destructor
     */
    ~PresetManager();

    /**
     * @brief Load preset directory
     * @param directory_path Path to directory containing preset files
     * @return true if loaded successfully, false otherwise
     */
    bool load_preset_directory(const std::string& directory_path);

    /**
     * @brief Add preset directory to search paths
     * @param directory_path Additional directory to search for presets
     * @return true if added successfully, false otherwise
     */
    bool add_preset_directory(const std::string& directory_path);

    /**
     * @brief Clear all preset directories
     */
    void clear_preset_directories();

    /**
     * @brief Get list of preset directories
     * @return Vector of preset directory paths
     */
    std::vector<std::string> get_preset_directories() const;

    /**
     * @brief Get all available presets
     * @return Vector of preset information
     */
    std::vector<PresetInfo> get_available_presets() const;

    /**
     * @brief Get presets by category
     * @param category Category name
     * @return Vector of presets in the specified category
     */
    std::vector<PresetInfo> get_presets_by_category(const std::string& category) const;

    /**
     * @brief Check if preset exists
     * @param preset_name Name of the preset
     * @return true if preset exists, false otherwise
     */
    bool preset_exists(const std::string& preset_name) const;

    /**
     * @brief Load preset by name
     * @param preset_name Name of the preset to load
     * @return Preset configuration as JSON, or null if not found
     */
    nlohmann::json load_preset(const std::string& preset_name);

    /**
     * @brief Load preset to config manager
     * @param preset_name Name of the preset
     * @param config_manager ConfigManager instance to load into
     * @return true if loaded successfully, false otherwise
     */
    bool load_preset_to_config(const std::string& preset_name, class ConfigManager& config_manager);

    /**
     * @brief Get preset metadata
     * @param preset_name Name of the preset
     * @return Preset metadata
     */
    PresetMetadata get_preset_metadata(const std::string& preset_name) const;

    /**
     * @brief Save preset
     * @param preset_name Name of the preset
     * @param config Configuration to save
     * @return true if saved successfully, false otherwise
     */
    bool save_preset(const std::string& preset_name, const nlohmann::json& config);

    /**
     * @brief Save preset with metadata
     * @param preset_name Name of the preset
     * @param config Configuration to save
     * @param metadata Preset metadata
     * @return true if saved successfully, false otherwise
     */
    bool save_preset(const std::string& preset_name, const nlohmann::json& config,
                    const PresetMetadata& metadata);

    /**
     * @brief Delete preset
     * @param preset_name Name of the preset to delete
     * @return true if deleted successfully, false otherwise
     */
    bool delete_preset(const std::string& preset_name);

    /**
     * @brief Rename preset
     * @param old_name Current preset name
     * @param new_name New preset name
     * @return true if renamed successfully, false otherwise
     */
    bool rename_preset(const std::string& old_name, const std::string& new_name);

    /**
     * @brief Get available categories
     * @return Vector of category names
     */
    std::vector<std::string> get_categories() const;

    /**
     * @brief Set preset category
     * @param preset_name Name of the preset
     * @param category Category name
     * @return true if set successfully, false otherwise
     */
    bool set_preset_category(const std::string& preset_name, const std::string& category);

    /**
     * @brief Get preset category
     * @param preset_name Name of the preset
     * @return Category name, or empty string if not set
     */
    std::string get_preset_category(const std::string& preset_name) const;

    /**
     * @brief Validate preset
     * @param preset_name Name of the preset
     * @return true if valid, false otherwise
     */
    bool validate_preset(const std::string& preset_name) const;

    /**
     * @brief Validate preset configuration
     * @param preset_config Configuration to validate
     * @return true if valid, false otherwise
     */
    bool validate_preset(const nlohmann::json& preset_config) const;

    /**
     * @brief Get preset validation errors
     * @param preset_name Name of the preset
     * @return Vector of validation errors
     */
    std::vector<ValidationError> get_preset_validation_errors(const std::string& preset_name) const;

    /**
     * @brief Get last error message
     * @return Last error message
     */
    std::string get_last_error() const;

private:
    std::vector<std::string> preset_directories_;
    std::unordered_map<std::string, PresetInfo> presets_;
    std::string last_error_;

    /**
     * @brief Set last error message
     * @param error Error message
     */
    void set_error(const std::string& error);

    /**
     * @brief Scan directory for presets
     * @param directory_path Directory to scan
     * @return true if scanned successfully, false otherwise
     */
    bool scan_directory(const std::string& directory_path);

    /**
     * @brief Load preset from file
     * @param file_path Path to preset file
     * @return Preset information, or empty if failed
     */
    PresetInfo load_preset_from_file(const std::string& file_path);

    /**
     * @brief Extract metadata from preset configuration
     * @param config Preset configuration
     * @return Extracted metadata
     */
    PresetMetadata extract_metadata(const nlohmann::json& config);

    /**
     * @brief Create default metadata for preset
     * @param preset_name Name of the preset
     * @return Default metadata
     */
    PresetMetadata create_default_metadata(const std::string& preset_name) const;

    /**
     * @brief Get full path for preset
     * @param preset_name Name of the preset
     * @return Full path to preset file, or empty string if not found
     */
    std::string get_preset_path(const std::string& preset_name) const;

    /**
     * @brief Validate preset file
     * @param file_path Path to preset file
     * @return true if valid, false otherwise
     */
    bool validate_preset_file(const std::string& file_path) const;
};

} // namespace gamepad_config