#pragma once

#include <string>

namespace {{namespace}} {

/**
 * @brief Main class for {{project_name}}
 */
class {{class_name}} {
public:
    /**
     * @brief Constructor
     */
    {{class_name}}();

    /**
     * @brief Destructor
     */
    ~{{class_name}}();

    /**
     * @brief Get version string
     * @return Version string
     */
    std::string get_version() const;

    /**
     * @brief Process input data
     * @param input Input data
     * @return Processed output
     */
    std::string process(const std::string& input);

private:
    std::string version_;
};

} // namespace {{namespace}}