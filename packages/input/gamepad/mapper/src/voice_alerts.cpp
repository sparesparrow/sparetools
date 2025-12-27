#include "voice_alerts.h"
#include "audio_backend.h"
#include <iostream>
#include <sstream>
#include <cstdlib>
#include <algorithm>
#include <chrono>
#include <thread>

namespace gamepad_mapper {

class VoiceAlerts::Impl {
public:
    Impl() : running_(false), speaking_(false), settings_(), audio_manager_(std::make_unique<AudioManager>()) {}

    ~Impl() {
        stop();
    }

    bool initialize() {
        // Check if espeak is available
        int result = std::system("which espeak > /dev/null 2>&1");
        if (result != 0) {
            std::cerr << "Warning: espeak not found. Voice alerts will be disabled." << std::endl;
            return false;
        }

        // Initialize audio manager
        if (!audio_manager_->initialize()) {
            std::cerr << "Warning: Failed to initialize audio manager. Voice alerts may not work properly." << std::endl;
        }

        std::cout << "Voice alerts system initialized successfully" << std::endl;
        return true;
    }

    bool start() {
        if (running_) {
            return true;
        }

        if (!settings_.enabled) {
            return false;
        }

        running_ = true;
        alert_thread_ = std::thread(&Impl::alert_loop, this);

        std::cout << "Voice alerts system started" << std::endl;
        return true;
    }

    void stop() {
        if (!running_) {
            return;
        }

        running_ = false;
        
        // Clear the queue
        {
            std::lock_guard<std::mutex> lock(queue_mutex_);
            while (!alert_queue_.empty()) {
                alert_queue_.pop();
            }
        }

        // Wait for thread to finish
        if (alert_thread_.joinable()) {
            alert_thread_.join();
        }

        std::cout << "Voice alerts system stopped" << std::endl;
    }

    void queue_alert(const VoiceAlert& alert) {
        if (!settings_.enabled) {
            return;
        }

        std::lock_guard<std::mutex> lock(queue_mutex_);
        
        // Check queue size limit
        if (alert_queue_.size() >= static_cast<size_t>(settings_.max_queue_size)) {
            // Remove oldest low priority alert
            std::queue<VoiceAlert> temp_queue;
            bool removed = false;
            
            while (!alert_queue_.empty()) {
                const auto& front_alert = alert_queue_.front();
                if (!removed && front_alert.priority == AlertPriority::LOW) {
                    alert_queue_.pop();
                    removed = true;
                } else {
                    temp_queue.push(front_alert);
                    alert_queue_.pop();
                }
            }
            
            alert_queue_ = std::move(temp_queue);
        }

        // Interrupt current speech if high priority
        if (alert.priority == AlertPriority::HIGH || alert.priority == AlertPriority::CRITICAL) {
            if (speaking_ && settings_.interrupt_on_high_priority) {
                interrupt_current_speech();
            }
        }

        alert_queue_.push(alert);
        queue_cv_.notify_one();
    }

    void queue_alert(AlertType type, const std::string& message, AlertPriority priority) {
        VoiceAlert alert(type, message, priority);
        queue_alert(alert);
    }

    void speak_immediately(const std::string& message) {
        VoiceAlert alert(AlertType::CUSTOM, message, AlertPriority::HIGH);
        alert.interrupt_current = true;
        queue_alert(alert);
    }

    void speak_immediately(AlertType type, const std::string& message) {
        VoiceAlert alert(type, message, AlertPriority::HIGH);
        alert.interrupt_current = true;
        queue_alert(alert);
    }

    void set_voice_settings(const VoiceSettings& settings) {
        std::lock_guard<std::mutex> lock(settings_mutex_);
        settings_ = settings;
    }

    VoiceSettings get_voice_settings() const {
        std::lock_guard<std::mutex> lock(settings_mutex_);
        return settings_;
    }

    void set_enabled(bool enabled) {
        std::lock_guard<std::mutex> lock(settings_mutex_);
        settings_.enabled = enabled;
    }

    bool is_enabled() const {
        std::lock_guard<std::mutex> lock(settings_mutex_);
        return settings_.enabled;
    }

    void set_volume(float volume) {
        std::lock_guard<std::mutex> lock(settings_mutex_);
        settings_.default_volume = std::clamp(volume, 0.0f, 1.0f);
    }

    void set_speed(float speed) {
        std::lock_guard<std::mutex> lock(settings_mutex_);
        settings_.default_speed = std::clamp(speed, 0.1f, 3.0f);
    }

    void set_voice(const std::string& voice_name) {
        std::lock_guard<std::mutex> lock(settings_mutex_);
        settings_.default_voice = voice_name;
    }

    void clear_queue() {
        std::lock_guard<std::mutex> lock(queue_mutex_);
        while (!alert_queue_.empty()) {
            alert_queue_.pop();
        }
    }

    size_t queue_size() const {
        std::lock_guard<std::mutex> lock(queue_mutex_);
        return alert_queue_.size();
    }

    bool is_speaking() const {
        return speaking_;
    }

    void register_alert_callback(VoiceAlertCallback callback) {
        std::lock_guard<std::mutex> lock(callback_mutex_);
        alert_callbacks_.push_back(callback);
    }

    void alert_controller_connected(const std::string& controller_name) {
        std::string message = "Controller connected: " + controller_name;
        queue_alert(AlertType::CONNECTION, message, AlertPriority::NORMAL);
    }

    void alert_controller_disconnected(const std::string& controller_name) {
        std::string message = "Controller disconnected: " + controller_name;
        queue_alert(AlertType::DISCONNECTION, message, AlertPriority::NORMAL);
    }

    void alert_error(const std::string& error_message) {
        queue_alert(AlertType::ERROR, error_message, AlertPriority::HIGH);
    }

    void alert_status_update(const std::string& status) {
        queue_alert(AlertType::STATUS_UPDATE, status, AlertPriority::LOW);
    }

    void alert_notification(const std::string& notification) {
        queue_alert(AlertType::NOTIFICATION, notification, AlertPriority::NORMAL);
    }

private:
    void alert_loop() {
        while (running_) {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            queue_cv_.wait(lock, [this] { return !running_ || !alert_queue_.empty(); });

            if (!running_) {
                break;
            }

            if (alert_queue_.empty()) {
                continue;
            }

            VoiceAlert alert = alert_queue_.front();
            alert_queue_.pop();
            lock.unlock();

            // Notify callbacks
            notify_callbacks(alert);

            // Speak the alert
            speak_alert(alert);
        }
    }

    void speak_alert(const VoiceAlert& alert) {
        if (alert.interrupt_current && speaking_) {
            interrupt_current_speech();
        }

        speaking_ = true;

        // Use audio manager for better audio control
        if (audio_manager_) {
            std::string voice = alert.voice_name;
            if (voice.empty() || voice == "default") {
                std::lock_guard<std::mutex> lock(settings_mutex_);
                voice = settings_.default_voice;
            }

            float speed = (alert.speed > 0) ? alert.speed : settings_.default_speed;
            float volume = (alert.volume > 0) ? alert.volume : settings_.default_volume;

            // Set volume on audio manager
            audio_manager_->set_volume(volume);

            // Use audio manager's TTS function
            bool success = audio_manager_->play_text_to_speech(alert.message, voice);
            if (!success) {
                std::cerr << "Failed to play text-to-speech: " << alert.message << std::endl;
            }
        } else {
            // Fallback to direct espeak command
            std::stringstream cmd;
            cmd << "espeak";
            
            // Voice settings
            {
                std::lock_guard<std::mutex> lock(settings_mutex_);
                if (!alert.voice_name.empty() && alert.voice_name != "default") {
                    cmd << " -v " << alert.voice_name;
                } else if (!settings_.default_voice.empty() && settings_.default_voice != "default") {
                    cmd << " -v " << settings_.default_voice;
                }

                float speed = (alert.speed > 0) ? alert.speed : settings_.default_speed;
                cmd << " -s " << static_cast<int>(speed * 100);

                float volume = (alert.volume > 0) ? alert.volume : settings_.default_volume;
                cmd << " -a " << static_cast<int>(volume * 200);
            }

            // Add message
            cmd << " \"" << alert.message << "\"";

            // Execute espeak
            int result = std::system(cmd.str().c_str());
            if (result != 0) {
                std::cerr << "Failed to execute espeak command: " << cmd.str() << std::endl;
            }
        }

        speaking_ = false;
    }

    void interrupt_current_speech() {
        if (audio_manager_) {
            audio_manager_->stop_playback();
        } else {
            // Kill any running espeak processes
            std::system("pkill -f espeak > /dev/null 2>&1");
        }
        speaking_ = false;
    }

    void notify_callbacks(const VoiceAlert& alert) {
        std::lock_guard<std::mutex> lock(callback_mutex_);
        for (const auto& callback : alert_callbacks_) {
            try {
                callback(alert);
            } catch (const std::exception& e) {
                std::cerr << "Error in voice alert callback: " << e.what() << std::endl;
            }
        }
    }

    std::atomic<bool> running_;
    std::atomic<bool> speaking_;
    std::thread alert_thread_;
    
    mutable std::mutex settings_mutex_;
    VoiceSettings settings_;
    
    mutable std::mutex queue_mutex_;
    std::queue<VoiceAlert> alert_queue_;
    std::condition_variable queue_cv_;
    
    mutable std::mutex callback_mutex_;
    std::vector<VoiceAlertCallback> alert_callbacks_;
    
    // Audio manager for better audio control
    std::unique_ptr<AudioManager> audio_manager_;
};

// Public interface implementation
VoiceAlerts::VoiceAlerts() : impl_(std::make_unique<Impl>()) {}
VoiceAlerts::~VoiceAlerts() = default;

bool VoiceAlerts::initialize() { return impl_->initialize(); }
bool VoiceAlerts::start() { return impl_->start(); }
void VoiceAlerts::stop() { impl_->stop(); }
void VoiceAlerts::queue_alert(const VoiceAlert& alert) { impl_->queue_alert(alert); }
void VoiceAlerts::queue_alert(AlertType type, const std::string& message, AlertPriority priority) { 
    impl_->queue_alert(type, message, priority); 
}
void VoiceAlerts::speak_immediately(const std::string& message) { impl_->speak_immediately(message); }
void VoiceAlerts::speak_immediately(AlertType type, const std::string& message) { 
    impl_->speak_immediately(type, message); 
}
void VoiceAlerts::set_voice_settings(const VoiceSettings& settings) { impl_->set_voice_settings(settings); }
VoiceSettings VoiceAlerts::get_voice_settings() const { return impl_->get_voice_settings(); }
void VoiceAlerts::set_enabled(bool enabled) { impl_->set_enabled(enabled); }
bool VoiceAlerts::is_enabled() const { return impl_->is_enabled(); }
void VoiceAlerts::set_volume(float volume) { impl_->set_volume(volume); }
void VoiceAlerts::set_speed(float speed) { impl_->set_speed(speed); }
void VoiceAlerts::set_voice(const std::string& voice_name) { impl_->set_voice(voice_name); }
void VoiceAlerts::clear_queue() { impl_->clear_queue(); }
size_t VoiceAlerts::queue_size() const { return impl_->queue_size(); }
bool VoiceAlerts::is_speaking() const { return impl_->is_speaking(); }
void VoiceAlerts::register_alert_callback(VoiceAlertCallback callback) { impl_->register_alert_callback(callback); }
void VoiceAlerts::alert_controller_connected(const std::string& controller_name) { 
    impl_->alert_controller_connected(controller_name); 
}
void VoiceAlerts::alert_controller_disconnected(const std::string& controller_name) { 
    impl_->alert_controller_disconnected(controller_name); 
}
void VoiceAlerts::alert_error(const std::string& error_message) { impl_->alert_error(error_message); }
void VoiceAlerts::alert_status_update(const std::string& status) { impl_->alert_status_update(status); }
void VoiceAlerts::alert_notification(const std::string& notification) { impl_->alert_notification(notification); }

} // namespace gamepad_mapper