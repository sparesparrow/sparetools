#pragma once

#include <string>
#include <vector>
#include <memory>
#include <atomic>
#include <mutex>
#include <functional>

namespace gamepad_mapper {

// Audio device information
struct AudioDevice {
    std::string name;
    std::string description;
    std::string device_id;
    bool is_default;
    bool is_available;
    int channels;
    int sample_rate;
    
    AudioDevice() : is_default(false), is_available(false), channels(2), sample_rate(44100) {}
};

// Audio format specification
struct AudioFormat {
    int sample_rate;
    int channels;
    int bits_per_sample;
    bool is_float;
    
    AudioFormat() : sample_rate(44100), channels(2), bits_per_sample(16), is_float(false) {}
};

// Audio backend types
enum class AudioBackendType {
    ALSA,
    PULSEAUDIO,
    PIPE,  // For espeak pipe output
    NONE
};

// Audio backend interface
class AudioBackend {
public:
    virtual ~AudioBackend() = default;
    
    virtual bool initialize() = 0;
    virtual void cleanup() = 0;
    
    virtual bool is_available() const = 0;
    virtual std::vector<AudioDevice> get_available_devices() const = 0;
    virtual AudioDevice get_default_device() const = 0;
    
    virtual bool set_device(const std::string& device_id) = 0;
    virtual bool set_format(const AudioFormat& format) = 0;
    
    virtual bool play_audio(const std::vector<uint8_t>& audio_data) = 0;
    virtual bool play_audio_stream(const std::string& command) = 0;
    
    virtual void set_volume(float volume) = 0;
    virtual float get_volume() const = 0;
    
    virtual bool is_playing() const = 0;
    virtual void stop_playback() = 0;
};

// Audio manager for handling multiple backends
class AudioManager {
public:
    AudioManager();
    ~AudioManager();
    
    // Initialize audio system
    bool initialize();
    void cleanup();
    
    // Backend management
    bool set_preferred_backend(AudioBackendType type);
    AudioBackendType get_current_backend() const;
    std::vector<AudioBackendType> get_available_backends() const;
    
    // Device management
    std::vector<AudioDevice> get_available_devices() const;
    AudioDevice get_default_device() const;
    bool set_output_device(const std::string& device_id);
    
    // Audio playback
    bool play_audio(const std::vector<uint8_t>& audio_data);
    bool play_audio_stream(const std::string& command);
    bool play_text_to_speech(const std::string& text, const std::string& voice = "default");
    
    // Audio control
    void set_volume(float volume);
    float get_volume() const;
    void set_muted(bool muted);
    bool is_muted() const;
    
    // Playback control
    bool is_playing() const;
    void stop_playback();
    void pause_playback();
    void resume_playback();
    
    // Audio mixing
    void set_mixing_enabled(bool enabled);
    bool is_mixing_enabled() const;
    
    // Callbacks
    using PlaybackFinishedCallback = std::function<void()>;
    void register_playback_finished_callback(PlaybackFinishedCallback callback);
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace gamepad_mapper