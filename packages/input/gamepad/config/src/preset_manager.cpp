#include "preset_manager.h"
#include "config_manager.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <algorithm>

namespace fs = std::filesystem;

namespace gamepad_config {

PresetManager::PresetManager() = default;

PresetManager::~PresetManager() = default;

bool PresetManager::load_preset_directory(const std::string& directory_path) {
    clear_preset_directories();
    return add_preset_directory(directory_path);
}

bool PresetManager::add_preset_directory(const std::string& directory_path) {
    if (!fs::exists(directory_path)) {
        set_error("Preset directory does not exist: " + directory_path);
        return false;
    }

    if (!fs::is_directory(directory_path)) {
        set_error("Path is not a directory: " + directory_path);
        return false;
    }

    // Check if directory is already added
    if (std::find(preset_directories_.begin(), preset_directories_.end(), directory_path)
        != preset_directories_.end()) {
        return true; // Already added
    }

    preset_directories_.push_back(directory_path);

    if (!scan_directory(directory_path)) {
        set_error("Failed to scan preset directory: " + directory_path);
        return false;
    }

    return true;
}

void PresetManager::clear_preset_directories() {
    preset_directories_.clear();
    presets_.clear();
    last_error_.clear();
}

std::vector<std::string> PresetManager::get_preset_directories() const {
    return preset_directories_;
}

std::vector<PresetInfo> PresetManager::get_available_presets() const {
    std::vector<PresetInfo> result;
    for (const auto& [name, info] : presets_) {
        result.push_back(info);
    }
    return result;
}

std::vector<PresetInfo> PresetManager::get_presets_by_category(const std::string& category) const {
    std::vector<PresetInfo> result;
    for (const auto& [name, info] : presets_) {
        if (info.metadata.category == category) {
            result.push_back(info);
        }
    }
    return result;
}

bool PresetManager::preset_exists(const std::string& preset_name) const {
    return presets_.find(preset_name) != presets_.end();
}

nlohmann::json PresetManager::load_preset(const std::string& preset_name) {
    if (!preset_exists(preset_name)) {
        set_error("Preset does not exist: " + preset_name);
        return nlohmann::json();
    }

    const auto& info = presets_.at(preset_name);
    try {
        std::ifstream file(info.path);
        if (!file.is_open()) {
            set_error("Failed to open preset file: " + info.path);
            return nlohmann::json();
        }

        nlohmann::json config;
        file >> config;
        return config;
    } catch (const std::exception& e) {
        set_error("Failed to load preset '" + preset_name + "': " + e.what());
        return nlohmann::json();
    }
}

bool PresetManager::load_preset_to_config(const std::string& preset_name, ConfigManager& config_manager) {
    nlohmann::json preset_config = load_preset(preset_name);
    if (preset_config.is_null()) {
        return false;
    }

    return config_manager.set_config(preset_config);
}

PresetMetadata PresetManager::get_preset_metadata(const std::string& preset_name) const {
    if (!preset_exists(preset_name)) {
        return create_default_metadata(preset_name);
    }

    return presets_.at(preset_name).metadata;
}

bool PresetManager::save_preset(const std::string& preset_name, const nlohmann::json& config) {
    PresetMetadata metadata = create_default_metadata(preset_name);
    return save_preset(preset_name, config, metadata);
}

bool PresetManager::save_preset(const std::string& preset_name, const nlohmann::json& config,
                               const PresetMetadata& metadata) {
    if (preset_directories_.empty()) {
        set_error("No preset directories configured");
        return false;
    }

    // Use first directory for saving
    std::string save_path = preset_directories_[0] + "/" + preset_name + ".json";

    try {
        // Create directory if it doesn't exist
        fs::create_directories(fs::path(save_path).parent_path());

        // Save configuration
        nlohmann::json full_config = config;
        full_config["_metadata"] = {
            {"name", metadata.name},
            {"description", metadata.description},
            {"category", metadata.category},
            {"author", metadata.author},
            {"version", metadata.version},
            {"created_date", metadata.created_date},
            {"tags", metadata.tags}
        };

        std::ofstream file(save_path);
        if (!file.is_open()) {
            set_error("Failed to open file for writing: " + save_path);
            return false;
        }

        file << full_config.dump(2);

        // Update internal state
        PresetInfo info;
        info.name = preset_name;
        info.path = save_path;
        info.metadata = metadata;
        info.is_valid = validate_preset(config);
        presets_[preset_name] = info;

        return true;
    } catch (const std::exception& e) {
        set_error("Failed to save preset '" + preset_name + "': " + e.what());
        return false;
    }
}

bool PresetManager::delete_preset(const std::string& preset_name) {
    if (!preset_exists(preset_name)) {
        set_error("Preset does not exist: " + preset_name);
        return false;
    }

    const auto& info = presets_.at(preset_name);
    try {
        if (fs::exists(info.path)) {
            fs::remove(info.path);
        }
        presets_.erase(preset_name);
        return true;
    } catch (const std::exception& e) {
        set_error("Failed to delete preset '" + preset_name + "': " + e.what());
        return false;
    }
}

bool PresetManager::rename_preset(const std::string& old_name, const std::string& new_name) {
    if (!preset_exists(old_name)) {
        set_error("Preset does not exist: " + old_name);
        return false;
    }

    if (preset_exists(new_name)) {
        set_error("Preset already exists: " + new_name);
        return false;
    }

    const auto& old_info = presets_.at(old_name);
    std::string new_path = fs::path(old_info.path).parent_path() / (new_name + ".json");

    try {
        fs::rename(old_info.path, new_path);

        PresetInfo new_info = old_info;
        new_info.name = new_name;
        new_info.path = new_path.string();
        new_info.metadata.name = new_name;

        presets_.erase(old_name);
        presets_[new_name] = new_info;

        return true;
    } catch (const std::exception& e) {
        set_error("Failed to rename preset: " + e.what());
        return false;
    }
}

std::vector<std::string> PresetManager::get_categories() const {
    std::vector<std::string> categories;
    for (const auto& [name, info] : presets_) {
        if (!info.metadata.category.empty() &&
            std::find(categories.begin(), categories.end(), info.metadata.category) == categories.end()) {
            categories.push_back(info.metadata.category);
        }
    }
    return categories;
}

bool PresetManager::set_preset_category(const std::string& preset_name, const std::string& category) {
    if (!preset_exists(preset_name)) {
        set_error("Preset does not exist: " + preset_name);
        return false;
    }

    presets_[preset_name].metadata.category = category;

    // Update the file
    nlohmann::json config = load_preset(preset_name);
    if (!config.is_null() && config.contains("_metadata")) {
        config["_metadata"]["category"] = category;
        return save_preset(preset_name, config, presets_[preset_name].metadata);
    }

    return true;
}

std::string PresetManager::get_preset_category(const std::string& preset_name) const {
    if (!preset_exists(preset_name)) {
        return "";
    }

    return presets_.at(preset_name).metadata.category;
}

bool PresetManager::validate_preset(const std::string& preset_name) const {
    nlohmann::json config = load_preset(preset_name);
    return validate_preset(config);
}

bool PresetManager::validate_preset(const nlohmann::json& preset_config) const {
    if (!preset_config.is_object()) {
        return false;
    }

    // Basic validation - check for required sections
    return preset_config.contains("mappings");
}

std::vector<ValidationError> PresetManager::get_preset_validation_errors(const std::string& preset_name) const {
    std::vector<ValidationError> errors;
    nlohmann::json config = load_preset(preset_name);

    if (!config.is_object()) {
        errors.push_back({"root", "Preset must be a JSON object", config.dump()});
        return errors;
    }

    if (!config.contains("mappings")) {
        errors.push_back({"mappings", "Mappings section is required", ""});
    }

    return errors;
}

std::string PresetManager::get_last_error() const {
    return last_error_;
}

void PresetManager::set_error(const std::string& error) {
    last_error_ = error;
    std::cerr << "PresetManager Error: " << error << std::endl;
}

bool PresetManager::scan_directory(const std::string& directory_path) {
    try {
        for (const auto& entry : fs::directory_iterator(directory_path)) {
            if (entry.is_regular_file() && entry.path().extension() == ".json") {
                PresetInfo info = load_preset_from_file(entry.path().string());
                if (!info.name.empty()) {
                    presets_[info.name] = info;
                }
            }
        }
        return true;
    } catch (const std::exception& e) {
        set_error("Failed to scan directory '" + directory_path + "': " + e.what());
        return false;
    }
}

PresetInfo PresetManager::load_preset_from_file(const std::string& file_path) {
    PresetInfo info;
    info.path = file_path;
    info.is_valid = false;

    try {
        std::ifstream file(file_path);
        if (!file.is_open()) {
            return info;
        }

        nlohmann::json config;
        file >> config;

        if (!config.is_object()) {
            return info;
        }

        // Extract preset name from filename
        fs::path path(file_path);
        std::string filename = path.filename().string();
        if (filename.size() > 5 && filename.substr(filename.size() - 5) == ".json") {
            info.name = filename.substr(0, filename.size() - 5);
        }

        // Extract metadata
        info.metadata = extract_metadata(config);
        info.is_valid = validate_preset(config);

    } catch (const std::exception& e) {
        // File couldn't be parsed, return empty info
    }

    return info;
}

PresetMetadata PresetManager::extract_metadata(const nlohmann::json& config) {
    PresetMetadata metadata;

    if (config.contains("_metadata") && config["_metadata"].is_object()) {
        const auto& meta = config["_metadata"];
        metadata.name = meta.value("name", "");
        metadata.description = meta.value("description", "");
        metadata.category = meta.value("category", "");
        metadata.author = meta.value("author", "");
        metadata.version = meta.value("version", "1.0.0");
        metadata.created_date = meta.value("created_date", "");

        if (meta.contains("tags") && meta["tags"].is_array()) {
            for (const auto& tag : meta["tags"]) {
                if (tag.is_string()) {
                    metadata.tags.push_back(tag);
                }
            }
        }
    }

    return metadata;
}

PresetMetadata PresetManager::create_default_metadata(const std::string& preset_name) const {
    PresetMetadata metadata;
    metadata.name = preset_name;
    metadata.version = "1.0.0";

    // Try to infer category from name
    if (preset_name.find("gaming") != std::string::npos ||
        preset_name.find("game") != std::string::npos) {
        metadata.category = "gaming";
    } else if (preset_name.find("accessibility") != std::string::npos ||
               preset_name.find("disabled") != std::string::npos) {
        metadata.category = "accessibility";
    } else if (preset_name.find("professional") != std::string::npos ||
               preset_name.find("work") != std::string::npos) {
        metadata.category = "professional";
    }

    return metadata;
}

std::string PresetManager::get_preset_path(const std::string& preset_name) const {
    if (!preset_exists(preset_name)) {
        return "";
    }

    return presets_.at(preset_name).path;
}

bool PresetManager::validate_preset_file(const std::string& file_path) const {
    PresetInfo info = load_preset_from_file(file_path);
    return info.is_valid;
}

} // namespace gamepad_config