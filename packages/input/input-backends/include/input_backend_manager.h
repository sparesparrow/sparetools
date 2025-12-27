#pragma once

#include <memory>
#include <string>
#include <vector>
#include "backends/input_simulator.h"

namespace input_backends {

/**
 * @brief Manager class for input backend selection and creation
 *
 * The InputBackendManager automatically detects available input backends
 * on the system and provides a unified interface for creating input simulators.
 * It follows a priority order for backend selection based on reliability and features.
 */
class InputBackendManager {
public:
    /**
     * @brief Initialize the backend manager
     * @return true if initialization successful, false otherwise
     */
    bool initialize();

    /**
     * @brief Shutdown the backend manager and clean up resources
     */
    void shutdown();

    /**
     * @brief Check if the manager is initialized
     * @return true if initialized, false otherwise
     */
    bool is_initialized() const;

    /**
     * @brief Create the best available input simulator
     *
     * This method tries backends in the following priority order:
     * 1. X11 (most compatible, widely available)
     * 2. Wayland (modern, but requires Wayland session)
     * 3. KDE (KDE-specific optimizations)
     * 4. SDL2 (cross-platform fallback)
     * 5. UInput (kernel-level, requires permissions)
     *
     * @return Unique pointer to the created simulator, or nullptr if none available
     */
    std::unique_ptr<InputSimulator> create_best_simulator();

    /**
     * @brief Create a specific input simulator by name
     * @param backend_name Name of the backend ("x11", "wayland", "kde", "sdl2", "uinput")
     * @return Unique pointer to the created simulator, or nullptr if not available
     */
    std::unique_ptr<InputSimulator> create_simulator(const std::string& backend_name);

    /**
     * @brief Get list of available backend names
     * @return Vector of available backend names
     */
    std::vector<std::string> get_available_backends() const;

    /**
     * @brief Check if a specific backend is available
     * @param backend_name Name of the backend to check
     * @return true if available, false otherwise
     */
    bool is_backend_available(const std::string& backend_name) const;

    /**
     * @brief Set preferred backend for create_best_simulator()
     * @param backend_name Name of the preferred backend
     * @return true if preference set, false if backend not available
     */
    bool set_preferred_backend(const std::string& backend_name);

    /**
     * @brief Get the currently preferred backend name
     * @return Preferred backend name, or empty string if none set
     */
    std::string get_preferred_backend() const;

    /**
     * @brief Get backend capabilities and information
     * @param backend_name Name of the backend
     * @return BackendCapabilities struct with information about the backend
     */
    BackendCapabilities get_backend_capabilities(const std::string& backend_name) const;

    /**
     * @brief Get last error message
     * @return Last error message, or empty string if no error
     */
    std::string get_last_error() const;

private:
    bool initialized_ = false;
    std::string preferred_backend_;
    std::string last_error_;

    // Backend availability flags (detected at runtime)
    bool x11_available_ = false;
    bool wayland_available_ = false;
    bool kde_available_ = false;
    bool sdl2_available_ = false;
    bool uinput_available_ = false;

    /**
     * @brief Detect which backends are available on this system
     */
    void detect_available_backends();

    /**
     * @brief Set last error message
     * @param error Error message
     */
    void set_error(const std::string& error);
};

// Factory functions for creating simulators
std::unique_ptr<InputSimulator> create_x11_simulator();
std::unique_ptr<InputSimulator> create_wayland_simulator();
std::unique_ptr<InputSimulator> create_kde_simulator();
std::unique_ptr<InputSimulator> create_sdl2_simulator();
std::unique_ptr<InputSimulator> create_uinput_simulator();

} // namespace input_backends