#include "input_backend_manager.h"
#include <algorithm>
#include <iostream>
#include <cstdlib>
#include <unistd.h>

#ifdef WITH_X11
#include "backends/x11_simulator.h"
#endif

#ifdef WITH_WAYLAND
#include "backends/wayland_simulator.h"
#endif

#ifdef WITH_KDE
#include "backends/kde_simulator.h"
#endif

#ifdef WITH_SDL2
#include "backends/sdl2_simulator.h"
#endif

#ifdef WITH_UINPUT
#include "backends/uinput_simulator.h"
#endif

namespace input_backends {

bool InputBackendManager::initialize() {
    if (initialized_) {
        return true;
    }

    detect_available_backends();
    initialized_ = true;
    return true;
}

void InputBackendManager::shutdown() {
    initialized_ = false;
    preferred_backend_.clear();
    last_error_.clear();
}

bool InputBackendManager::is_initialized() const {
    return initialized_;
}

std::unique_ptr<InputSimulator> InputBackendManager::create_best_simulator() {
    if (!initialized_) {
        set_error("Backend manager not initialized");
        return nullptr;
    }

    // Priority order for backend selection
    std::vector<std::string> priority_order = {"x11", "wayland", "kde", "sdl2", "uinput"};

    // If preferred backend is set and available, use it first
    if (!preferred_backend_.empty() && is_backend_available(preferred_backend_)) {
        auto simulator = create_simulator(preferred_backend_);
        if (simulator) {
            return simulator;
        }
    }

    // Try backends in priority order
    for (const auto& backend : priority_order) {
        if (is_backend_available(backend)) {
            auto simulator = create_simulator(backend);
            if (simulator) {
                return simulator;
            }
        }
    }

    set_error("No suitable input backend available");
    return nullptr;
}

std::unique_ptr<InputSimulator> InputBackendManager::create_simulator(const std::string& backend_name) {
    if (!initialized_) {
        set_error("Backend manager not initialized");
        return nullptr;
    }

    if (!is_backend_available(backend_name)) {
        set_error("Backend '" + backend_name + "' is not available");
        return nullptr;
    }

#ifdef WITH_X11
    if (backend_name == "x11") {
        return create_x11_simulator();
    }
#endif

#ifdef WITH_WAYLAND
    if (backend_name == "wayland") {
        return create_wayland_simulator();
    }
#endif

#ifdef WITH_KDE
    if (backend_name == "kde") {
        return create_kde_simulator();
    }
#endif

#ifdef WITH_SDL2
    if (backend_name == "sdl2") {
        return create_sdl2_simulator();
    }
#endif

#ifdef WITH_UINPUT
    if (backend_name == "uinput") {
        return create_uinput_simulator();
    }
#endif

    set_error("Unknown backend: " + backend_name);
    return nullptr;
}

std::vector<std::string> InputBackendManager::get_available_backends() const {
    std::vector<std::string> available;

    if (x11_available_) available.push_back("x11");
    if (wayland_available_) available.push_back("wayland");
    if (kde_available_) available.push_back("kde");
    if (sdl2_available_) available.push_back("sdl2");
    if (uinput_available_) available.push_back("uinput");

    return available;
}

bool InputBackendManager::is_backend_available(const std::string& backend_name) const {
    if (backend_name == "x11") return x11_available_;
    if (backend_name == "wayland") return wayland_available_;
    if (backend_name == "kde") return kde_available_;
    if (backend_name == "sdl2") return sdl2_available_;
    if (backend_name == "uinput") return uinput_available_;

    return false;
}

bool InputBackendManager::set_preferred_backend(const std::string& backend_name) {
    if (!is_backend_available(backend_name)) {
        set_error("Preferred backend '" + backend_name + "' is not available");
        return false;
    }

    preferred_backend_ = backend_name;
    return true;
}

std::string InputBackendManager::get_preferred_backend() const {
    return preferred_backend_;
}

BackendCapabilities InputBackendManager::get_backend_capabilities(const std::string& backend_name) const {
    BackendCapabilities caps;
    caps.name = backend_name;
    caps.available = is_backend_available(backend_name);

    // Set capabilities based on backend type
    if (backend_name == "x11") {
        caps.supports_keyboard = true;
        caps.supports_mouse = true;
        caps.supports_absolute_mouse = true;
        caps.supports_relative_mouse = true;
        caps.requires_root = false;
        caps.performance_rating = 8; // Good performance
        caps.compatibility_rating = 9; // Widely compatible
    } else if (backend_name == "wayland") {
        caps.supports_keyboard = true;
        caps.supports_mouse = true;
        caps.supports_absolute_mouse = true;
        caps.supports_relative_mouse = true;
        caps.requires_root = false;
        caps.performance_rating = 7;
        caps.compatibility_rating = 6; // Limited to Wayland sessions
    } else if (backend_name == "kde") {
        caps.supports_keyboard = true;
        caps.supports_mouse = true;
        caps.supports_absolute_mouse = true;
        caps.supports_relative_mouse = true;
        caps.requires_root = false;
        caps.performance_rating = 8;
        caps.compatibility_rating = 5; // KDE-specific
    } else if (backend_name == "sdl2") {
        caps.supports_keyboard = true;
        caps.supports_mouse = true;
        caps.supports_absolute_mouse = true;
        caps.supports_relative_mouse = true;
        caps.requires_root = false;
        caps.performance_rating = 6;
        caps.compatibility_rating = 7;
    } else if (backend_name == "uinput") {
        caps.supports_keyboard = true;
        caps.supports_mouse = true;
        caps.supports_absolute_mouse = true;
        caps.supports_relative_mouse = true;
        caps.requires_root = true; // Requires /dev/uinput access
        caps.performance_rating = 9; // Best performance
        caps.compatibility_rating = 8;
    }

    return caps;
}

std::string InputBackendManager::get_last_error() const {
    return last_error_;
}

void InputBackendManager::detect_available_backends() {
    // Reset availability flags
    x11_available_ = false;
    wayland_available_ = false;
    kde_available_ = false;
    sdl2_available_ = false;
    uinput_available_ = false;

    // Detect X11 availability
#ifdef WITH_X11
    const char* display = std::getenv("DISPLAY");
    if (display && strlen(display) > 0) {
        x11_available_ = true;
    }
#endif

    // Detect Wayland availability
#ifdef WITH_WAYLAND
    const char* wayland_display = std::getenv("WAYLAND_DISPLAY");
    if (wayland_display && strlen(wayland_display) > 0) {
        wayland_available_ = true;
    }
#endif

    // Detect KDE availability
#ifdef WITH_KDE
    const char* kde_session = std::getenv("KDE_SESSION_VERSION");
    const char* desktop_session = std::getenv("XDG_CURRENT_DESKTOP");
    if ((kde_session && strlen(kde_session) > 0) ||
        (desktop_session && std::string(desktop_session).find("KDE") != std::string::npos)) {
        kde_available_ = true;
    }
#endif

    // Detect SDL2 availability
#ifdef WITH_SDL2
    // SDL2 is generally available if compiled in
    sdl2_available_ = true;
#endif

    // Detect UInput availability
#ifdef WITH_UINPUT
    if (access("/dev/uinput", W_OK) == 0) {
        uinput_available_ = true;
    }
#endif
}

void InputBackendManager::set_error(const std::string& error) {
    last_error_ = error;
    std::cerr << "InputBackendManager Error: " << error << std::endl;
}

// Factory function implementations
std::unique_ptr<InputSimulator> create_x11_simulator() {
#ifdef WITH_X11
    return std::make_unique<X11Simulator>();
#else
    return nullptr;
#endif
}

std::unique_ptr<InputSimulator> create_wayland_simulator() {
#ifdef WITH_WAYLAND
    return std::make_unique<WaylandSimulator>();
#else
    return nullptr;
#endif
}

std::unique_ptr<InputSimulator> create_kde_simulator() {
#ifdef WITH_KDE
    return std::make_unique<KDESimulator>();
#else
    return nullptr;
#endif
}

std::unique_ptr<InputSimulator> create_sdl2_simulator() {
#ifdef WITH_SDL2
    return std::make_unique<SDL2Simulator>();
#else
    return nullptr;
#endif
}

std::unique_ptr<InputSimulator> create_uinput_simulator() {
#ifdef WITH_UINPUT
    return std::make_unique<UInputSimulator>();
#else
    return nullptr;
#endif
}

} // namespace input_backends