#pragma once

#include <string>
#include <vector>
#include <memory>
#include <atomic>
#include <thread>
#include <mutex>
#include <queue>
#include <functional>

namespace gamepad_mapper {

// Voice alert types
enum class AlertType {
    CONNECTION,
    DISCONNECTION,
    ERROR,
    STATUS_UPDATE,
    NOTIFICATION,
    CUSTOM
};

// Voice alert priority
enum class AlertPriority {
    LOW,
    NORMAL,
    HIGH,
    CRITICAL
};

// Voice alert structure
struct VoiceAlert {
    AlertType type;
    AlertPriority priority;
    std::string message;
    std::string voice_name;
    float speed;
    float volume;
    bool interrupt_current;

    VoiceAlert(AlertType t, const std::string& msg, AlertPriority p = AlertPriority::NORMAL)
        : type(t), priority(p), message(msg), voice_name("default"), 
          speed(1.0f), volume(1.0f), interrupt_current(false) {}
};

// Voice settings
struct VoiceSettings {
    std::string default_voice;
    float default_speed;
    float default_volume;
    bool enabled;
    int max_queue_size;
    bool interrupt_on_high_priority;

    VoiceSettings() 
        : default_voice("default"), default_speed(1.0f), default_volume(1.0f),
          enabled(true), max_queue_size(10), interrupt_on_high_priority(true) {}
};

// Voice alerts callback function type
using VoiceAlertCallback = std::function<void(const VoiceAlert& alert)>;

// Voice alerts system
class VoiceAlerts {
public:
    VoiceAlerts();
    ~VoiceAlerts();

    // Initialize the voice alerts system
    bool initialize();

    // Start/stop the voice alerts system
    bool start();
    void stop();

    // Queue a voice alert
    void queue_alert(const VoiceAlert& alert);
    void queue_alert(AlertType type, const std::string& message, 
                    AlertPriority priority = AlertPriority::NORMAL);

    // Immediate voice alerts (high priority)
    void speak_immediately(const std::string& message);
    void speak_immediately(AlertType type, const std::string& message);

    // Voice settings
    void set_voice_settings(const VoiceSettings& settings);
    VoiceSettings get_voice_settings() const;

    // Voice control
    void set_enabled(bool enabled);
    bool is_enabled() const;
    void set_volume(float volume);
    void set_speed(float speed);
    void set_voice(const std::string& voice_name);

    // Queue management
    void clear_queue();
    size_t queue_size() const;
    bool is_speaking() const;

    // Register callback for alert events
    void register_alert_callback(VoiceAlertCallback callback);

    // Predefined alert messages
    void alert_controller_connected(const std::string& controller_name);
    void alert_controller_disconnected(const std::string& controller_name);
    void alert_error(const std::string& error_message);
    void alert_status_update(const std::string& status);
    void alert_notification(const std::string& notification);

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace gamepad_mapper