#include "audio_backend.h"
#include <iostream>
#include <cstring>
#include <cstdlib>
#include <thread>
#include <chrono>
#include <algorithm>

#ifdef WITH_ALSA
#include <alsa/asoundlib.h>
#endif

#ifdef WITH_PULSEAUDIO
#include <pulse/simple.h>
#include <pulse/error.h>
#include <pulse/context.h>
#include <pulse/introspect.h>
#endif

namespace gamepad_mapper {

// ALSA Backend Implementation
#ifdef WITH_ALSA
class ALSABackend : public AudioBackend {
public:
    ALSABackend() : pcm_handle_(nullptr), volume_(1.0f), playing_(false) {}
    
    ~ALSABackend() {
        cleanup();
    }
    
    bool initialize() override {
        int err = snd_pcm_open(&pcm_handle_, "default", SND_PCM_STREAM_PLAYBACK, 0);
        if (err < 0) {
            std::cerr << "ALSA: Cannot open audio device: " << snd_strerror(err) << std::endl;
            return false;
        }
        
        // Set default format
        AudioFormat default_format;
        if (!set_format(default_format)) {
            cleanup();
            return false;
        }
        
        return true;
    }
    
    void cleanup() override {
        if (pcm_handle_) {
            snd_pcm_close(pcm_handle_);
            pcm_handle_ = nullptr;
        }
    }
    
    bool is_available() const override {
        return pcm_handle_ != nullptr;
    }
    
    std::vector<AudioDevice> get_available_devices() const override {
        std::vector<AudioDevice> devices;
        
        // Get default device
        AudioDevice default_device;
        default_device.name = "Default ALSA Device";
        default_device.description = "Default ALSA audio output";
        default_device.device_id = "default";
        default_device.is_default = true;
        default_device.is_available = true;
        devices.push_back(default_device);
        
        return devices;
    }
    
    AudioDevice get_default_device() const override {
        AudioDevice device;
        device.name = "Default ALSA Device";
        device.device_id = "default";
        device.is_default = true;
        device.is_available = true;
        return device;
    }
    
    bool set_device(const std::string& device_id) override {
        if (pcm_handle_) {
            snd_pcm_close(pcm_handle_);
        }
        
        int err = snd_pcm_open(&pcm_handle_, device_id.c_str(), SND_PCM_STREAM_PLAYBACK, 0);
        if (err < 0) {
            std::cerr << "ALSA: Cannot open device " << device_id << ": " << snd_strerror(err) << std::endl;
            return false;
        }
        
        return true;
    }
    
    bool set_format(const AudioFormat& format) override {
        if (!pcm_handle_) return false;
        
        snd_pcm_hw_params_t* params;
        snd_pcm_hw_params_alloca(&params);
        
        int err = snd_pcm_hw_params_any(pcm_handle_, params);
        if (err < 0) {
            std::cerr << "ALSA: Cannot initialize hardware parameter structure: " << snd_strerror(err) << std::endl;
            return false;
        }
        
        err = snd_pcm_hw_params_set_access(pcm_handle_, params, SND_PCM_ACCESS_RW_INTERLEAVED);
        if (err < 0) {
            std::cerr << "ALSA: Cannot set access type: " << snd_strerror(err) << std::endl;
            return false;
        }
        
        snd_pcm_format_t alsa_format = SND_PCM_FORMAT_S16_LE;
        if (format.is_float) {
            alsa_format = SND_PCM_FORMAT_FLOAT_LE;
        } else if (format.bits_per_sample == 8) {
            alsa_format = SND_PCM_FORMAT_U8;
        } else if (format.bits_per_sample == 24) {
            alsa_format = SND_PCM_FORMAT_S24_LE;
        } else if (format.bits_per_sample == 32) {
            alsa_format = SND_PCM_FORMAT_S32_LE;
        }
        
        err = snd_pcm_hw_params_set_format(pcm_handle_, params, alsa_format);
        if (err < 0) {
            std::cerr << "ALSA: Cannot set sample format: " << snd_strerror(err) << std::endl;
            return false;
        }
        
        unsigned int rate = format.sample_rate;
        err = snd_pcm_hw_params_set_rate_near(pcm_handle_, params, &rate, 0);
        if (err < 0) {
            std::cerr << "ALSA: Cannot set sample rate: " << snd_strerror(err) << std::endl;
            return false;
        }
        
        err = snd_pcm_hw_params_set_channels(pcm_handle_, params, format.channels);
        if (err < 0) {
            std::cerr << "ALSA: Cannot set channel count: " << snd_strerror(err) << std::endl;
            return false;
        }
        
        err = snd_pcm_hw_params(pcm_handle_, params);
        if (err < 0) {
            std::cerr << "ALSA: Cannot set parameters: " << snd_strerror(err) << std::endl;
            return false;
        }
        
        return true;
    }
    
    bool play_audio(const std::vector<uint8_t>& audio_data) override {
        if (!pcm_handle_ || audio_data.empty()) return false;
        
        playing_ = true;
        
        snd_pcm_sframes_t frames_written = snd_pcm_writei(pcm_handle_, audio_data.data(), 
                                                         audio_data.size() / (2 * sizeof(int16_t)));
        
        if (frames_written < 0) {
            frames_written = snd_pcm_recover(pcm_handle_, frames_written, 0);
        }
        
        playing_ = false;
        return frames_written >= 0;
    }
    
    bool play_audio_stream(const std::string& command) override {
        // For ALSA, we'll use a pipe to espeak
        std::string full_command = command + " | aplay -f cd -";
        int result = std::system(full_command.c_str());
        return result == 0;
    }
    
    void set_volume(float volume) override {
        volume_ = std::clamp(volume, 0.0f, 1.0f);
    }
    
    float get_volume() const override {
        return volume_;
    }
    
    bool is_playing() const override {
        return playing_;
    }
    
    void stop_playback() override {
        if (pcm_handle_) {
            snd_pcm_drop(pcm_handle_);
        }
        playing_ = false;
    }
    
private:
    snd_pcm_t* pcm_handle_;
    float volume_;
    std::atomic<bool> playing_;
};
#endif

// PulseAudio Backend Implementation
#ifdef WITH_PULSEAUDIO
class PulseAudioBackend : public AudioBackend {
public:
    PulseAudioBackend() : context_(nullptr), simple_(nullptr), volume_(1.0f), playing_(false) {}
    
    ~PulseAudioBackend() {
        cleanup();
    }
    
    bool initialize() override {
        pa_mainloop* mainloop = pa_mainloop_new();
        if (!mainloop) {
            std::cerr << "PulseAudio: Failed to create mainloop" << std::endl;
            return false;
        }
        
        pa_mainloop_api* api = pa_mainloop_get_api(mainloop);
        context_ = pa_context_new(api, "gamepad-mapper");
        
        if (!context_) {
            std::cerr << "PulseAudio: Failed to create context" << std::endl;
            pa_mainloop_free(mainloop);
            return false;
        }
        
        pa_context_connect(context_, nullptr, PA_CONTEXT_NOFLAGS, nullptr);
        
        // Wait for connection
        int retry = 0;
        while (pa_context_get_state(context_) != PA_CONTEXT_READY && retry < 50) {
            pa_mainloop_iterate(mainloop, 1, nullptr);
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            retry++;
        }
        
        if (pa_context_get_state(context_) != PA_CONTEXT_READY) {
            std::cerr << "PulseAudio: Failed to connect to server" << std::endl;
            cleanup();
            return false;
        }
        
        pa_mainloop_free(mainloop);
        return true;
    }
    
    void cleanup() override {
        if (simple_) {
            pa_simple_free(simple_);
            simple_ = nullptr;
        }
        if (context_) {
            pa_context_disconnect(context_);
            pa_context_unref(context_);
            context_ = nullptr;
        }
    }
    
    bool is_available() const override {
        return context_ != nullptr;
    }
    
    std::vector<AudioDevice> get_available_devices() const override {
        std::vector<AudioDevice> devices;
        
        // This would require a more complex implementation to enumerate devices
        // For now, return a default device
        AudioDevice default_device;
        default_device.name = "Default PulseAudio Device";
        default_device.description = "Default PulseAudio audio output";
        default_device.device_id = "default";
        default_device.is_default = true;
        default_device.is_available = true;
        devices.push_back(default_device);
        
        return devices;
    }
    
    AudioDevice get_default_device() const override {
        AudioDevice device;
        device.name = "Default PulseAudio Device";
        device.device_id = "default";
        device.is_default = true;
        device.is_available = true;
        return device;
    }
    
    bool set_device(const std::string& device_id) override {
        // PulseAudio device selection would be implemented here
        return true;
    }
    
    bool set_format(const AudioFormat& format) override {
        // Format would be set when creating the simple connection
        return true;
    }
    
    bool play_audio(const std::vector<uint8_t>& audio_data) override {
        if (!context_ || audio_data.empty()) return false;
        
        pa_sample_spec spec;
        spec.format = PA_SAMPLE_S16LE;
        spec.channels = 2;
        spec.rate = 44100;
        
        int error;
        simple_ = pa_simple_new(nullptr, "gamepad-mapper", PA_STREAM_PLAYBACK, nullptr,
                               "gamepad-mapper", &spec, nullptr, nullptr, &error);
        
        if (!simple_) {
            std::cerr << "PulseAudio: Failed to create simple connection: " << pa_strerror(error) << std::endl;
            return false;
        }
        
        playing_ = true;
        
        int result = pa_simple_write(simple_, audio_data.data(), audio_data.size(), &error);
        if (result < 0) {
            std::cerr << "PulseAudio: Failed to write audio data: " << pa_strerror(error) << std::endl;
            playing_ = false;
            return false;
        }
        
        pa_simple_drain(simple_, &error);
        playing_ = false;
        
        return true;
    }
    
    bool play_audio_stream(const std::string& command) override {
        // For PulseAudio, we'll use a pipe to espeak
        std::string full_command = command + " | paplay";
        int result = std::system(full_command.c_str());
        return result == 0;
    }
    
    void set_volume(float volume) override {
        volume_ = std::clamp(volume, 0.0f, 1.0f);
    }
    
    float get_volume() const override {
        return volume_;
    }
    
    bool is_playing() const override {
        return playing_;
    }
    
    void stop_playback() override {
        if (simple_) {
            pa_simple_free(simple_);
            simple_ = nullptr;
        }
        playing_ = false;
    }
    
private:
    pa_context* context_;
    pa_simple* simple_;
    float volume_;
    std::atomic<bool> playing_;
};
#endif

// Pipe Backend Implementation (for espeak)
class PipeBackend : public AudioBackend {
public:
    PipeBackend() : volume_(1.0f), playing_(false) {}
    
    ~PipeBackend() {
        cleanup();
    }
    
    bool initialize() override {
        return true; // Pipe backend doesn't need initialization
    }
    
    void cleanup() override {
        stop_playback();
    }
    
    bool is_available() const override {
        return true; // Pipe is always available
    }
    
    std::vector<AudioDevice> get_available_devices() const override {
        std::vector<AudioDevice> devices;
        
        AudioDevice pipe_device;
        pipe_device.name = "Pipe Output";
        pipe_device.description = "Audio output through system pipe";
        pipe_device.device_id = "pipe";
        pipe_device.is_default = true;
        pipe_device.is_available = true;
        devices.push_back(pipe_device);
        
        return devices;
    }
    
    AudioDevice get_default_device() const override {
        AudioDevice device;
        device.name = "Pipe Output";
        device.device_id = "pipe";
        device.is_default = true;
        device.is_available = true;
        return device;
    }
    
    bool set_device(const std::string& device_id) override {
        return device_id == "pipe";
    }
    
    bool set_format(const AudioFormat& format) override {
        return true; // Pipe doesn't care about format
    }
    
    bool play_audio(const std::vector<uint8_t>& audio_data) override {
        // Pipe backend doesn't support raw audio data
        return false;
    }
    
    bool play_audio_stream(const std::string& command) override {
        playing_ = true;
        int result = std::system(command.c_str());
        playing_ = false;
        return result == 0;
    }
    
    void set_volume(float volume) override {
        volume_ = std::clamp(volume, 0.0f, 1.0f);
    }
    
    float get_volume() const override {
        return volume_;
    }
    
    bool is_playing() const override {
        return playing_;
    }
    
    void stop_playback() override {
        // Kill any running espeak processes
        std::system("pkill -f espeak > /dev/null 2>&1");
        playing_ = false;
    }
    
private:
    float volume_;
    std::atomic<bool> playing_;
};

// AudioManager Implementation
class AudioManager::Impl {
public:
    Impl() : current_backend_(AudioBackendType::NONE), volume_(1.0f), muted_(false), mixing_enabled_(true) {}
    
    ~Impl() {
        cleanup();
    }
    
    bool initialize() {
        // Try to initialize backends in order of preference
        std::vector<AudioBackendType> backends = {
#ifdef WITH_PULSEAUDIO
            AudioBackendType::PULSEAUDIO,
#endif
#ifdef WITH_ALSA
            AudioBackendType::ALSA,
#endif
            AudioBackendType::PIPE
        };
        
        for (auto backend_type : backends) {
            if (initialize_backend(backend_type)) {
                current_backend_ = backend_type;
                std::cout << "Audio backend initialized: " << static_cast<int>(backend_type) << std::endl;
                return true;
            }
        }
        
        std::cerr << "No audio backends available" << std::endl;
        return false;
    }
    
    void cleanup() {
        if (backend_) {
            backend_->cleanup();
            backend_.reset();
        }
        current_backend_ = AudioBackendType::NONE;
    }
    
    bool set_preferred_backend(AudioBackendType type) {
        if (initialize_backend(type)) {
            current_backend_ = type;
            return true;
        }
        return false;
    }
    
    AudioBackendType get_current_backend() const {
        return current_backend_;
    }
    
    std::vector<AudioBackendType> get_available_backends() const {
        std::vector<AudioBackendType> backends;
        
#ifdef WITH_PULSEAUDIO
        backends.push_back(AudioBackendType::PULSEAUDIO);
#endif
#ifdef WITH_ALSA
        backends.push_back(AudioBackendType::ALSA);
#endif
        backends.push_back(AudioBackendType::PIPE);
        
        return backends;
    }
    
    std::vector<AudioDevice> get_available_devices() const {
        if (backend_) {
            return backend_->get_available_devices();
        }
        return {};
    }
    
    AudioDevice get_default_device() const {
        if (backend_) {
            return backend_->get_default_device();
        }
        return AudioDevice();
    }
    
    bool set_output_device(const std::string& device_id) {
        if (backend_) {
            return backend_->set_device(device_id);
        }
        return false;
    }
    
    bool play_audio(const std::vector<uint8_t>& audio_data) {
        if (backend_ && !muted_) {
            return backend_->play_audio(audio_data);
        }
        return false;
    }
    
    bool play_audio_stream(const std::string& command) {
        if (backend_ && !muted_) {
            return backend_->play_audio_stream(command);
        }
        return false;
    }
    
    bool play_text_to_speech(const std::string& text, const std::string& voice) {
        std::stringstream cmd;
        cmd << "espeak";
        
        if (!voice.empty() && voice != "default") {
            cmd << " -v " << voice;
        }
        
        cmd << " -s 150 -a 200"; // Speed and amplitude
        cmd << " \"" << text << "\"";
        
        return play_audio_stream(cmd.str());
    }
    
    void set_volume(float volume) {
        volume_ = std::clamp(volume, 0.0f, 1.0f);
        if (backend_) {
            backend_->set_volume(volume_);
        }
    }
    
    float get_volume() const {
        return volume_;
    }
    
    void set_muted(bool muted) {
        muted_ = muted;
    }
    
    bool is_muted() const {
        return muted_;
    }
    
    bool is_playing() const {
        return backend_ && backend_->is_playing();
    }
    
    void stop_playback() {
        if (backend_) {
            backend_->stop_playback();
        }
    }
    
    void pause_playback() {
        // Implementation would depend on backend capabilities
        stop_playback();
    }
    
    void resume_playback() {
        // Implementation would depend on backend capabilities
    }
    
    void set_mixing_enabled(bool enabled) {
        mixing_enabled_ = enabled;
    }
    
    bool is_mixing_enabled() const {
        return mixing_enabled_;
    }
    
    void register_playback_finished_callback(PlaybackFinishedCallback callback) {
        std::lock_guard<std::mutex> lock(callback_mutex_);
        playback_finished_callbacks_.push_back(callback);
    }
    
private:
    bool initialize_backend(AudioBackendType type) {
        std::unique_ptr<AudioBackend> new_backend;
        
        switch (type) {
#ifdef WITH_PULSEAUDIO
            case AudioBackendType::PULSEAUDIO:
                new_backend = std::make_unique<PulseAudioBackend>();
                break;
#endif
#ifdef WITH_ALSA
            case AudioBackendType::ALSA:
                new_backend = std::make_unique<ALSABackend>();
                break;
#endif
            case AudioBackendType::PIPE:
                new_backend = std::make_unique<PipeBackend>();
                break;
            default:
                return false;
        }
        
        if (new_backend && new_backend->initialize()) {
            backend_ = std::move(new_backend);
            return true;
        }
        
        return false;
    }
    
    std::unique_ptr<AudioBackend> backend_;
    AudioBackendType current_backend_;
    float volume_;
    bool muted_;
    bool mixing_enabled_;
    
    mutable std::mutex callback_mutex_;
    std::vector<PlaybackFinishedCallback> playback_finished_callbacks_;
};

// Public interface implementation
AudioManager::AudioManager() : impl_(std::make_unique<Impl>()) {}
AudioManager::~AudioManager() = default;

bool AudioManager::initialize() { return impl_->initialize(); }
void AudioManager::cleanup() { impl_->cleanup(); }
bool AudioManager::set_preferred_backend(AudioBackendType type) { return impl_->set_preferred_backend(type); }
AudioBackendType AudioManager::get_current_backend() const { return impl_->get_current_backend(); }
std::vector<AudioBackendType> AudioManager::get_available_backends() const { return impl_->get_available_backends(); }
std::vector<AudioDevice> AudioManager::get_available_devices() const { return impl_->get_available_devices(); }
AudioDevice AudioManager::get_default_device() const { return impl_->get_default_device(); }
bool AudioManager::set_output_device(const std::string& device_id) { return impl_->set_output_device(device_id); }
bool AudioManager::play_audio(const std::vector<uint8_t>& audio_data) { return impl_->play_audio(audio_data); }
bool AudioManager::play_audio_stream(const std::string& command) { return impl_->play_audio_stream(command); }
bool AudioManager::play_text_to_speech(const std::string& text, const std::string& voice) { return impl_->play_text_to_speech(text, voice); }
void AudioManager::set_volume(float volume) { impl_->set_volume(volume); }
float AudioManager::get_volume() const { return impl_->get_volume(); }
void AudioManager::set_muted(bool muted) { impl_->set_muted(muted); }
bool AudioManager::is_muted() const { return impl_->is_muted(); }
bool AudioManager::is_playing() const { return impl_->is_playing(); }
void AudioManager::stop_playback() { impl_->stop_playback(); }
void AudioManager::pause_playback() { impl_->pause_playback(); }
void AudioManager::resume_playback() { impl_->resume_playback(); }
void AudioManager::set_mixing_enabled(bool enabled) { impl_->set_mixing_enabled(enabled); }
bool AudioManager::is_mixing_enabled() const { return impl_->is_mixing_enabled(); }
void AudioManager::register_playback_finished_callback(PlaybackFinishedCallback callback) { impl_->register_playback_finished_callback(callback); }

} // namespace gamepad_mapper