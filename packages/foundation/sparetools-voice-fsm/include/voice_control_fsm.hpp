#pragma once

#include <boost/sml.hpp>
#include <string>
#include <functional>

namespace sml = boost::sml;

struct VoiceControlContext {
    // Callbacks to worker threads
    std::function<void(const std::string&)> on_audio_ready;
    std::function<void(const std::string&)> on_intent_recognized;
    std::function<void(const std::string&)> on_response_ready;
    std::function<void()> on_playback_finished;

    // State data
    std::string last_transcription;
    std::string pending_response;
    bool wake_word_detected = false;
};

// Events
struct wake_word { std::string word; };
struct audio_recorded { std::string wav_path; };
struct text_transcribed { std::string text; };
struct intent_parsed { std::string tool; std::string args; };
struct command_executed { std::string result; };
struct response_ready { std::string text; };
struct playback_finished {};
struct error_occurred { std::string message; };

// States
auto idle = sml::state<class idle>;
auto listening = sml::state<class listening>;
auto processing = sml::state<class processing>;
auto speaking = sml::state<class speaking>;
auto error_state = sml::state<class error>;

// Guards
auto has_wake_word = [](const wake_word& e, VoiceControlContext& ctx) {
    return e.word == "hey mia" || e.word == "computer";
};

// Actions
auto start_recording = [](VoiceControlContext& ctx) {
    ctx.on_audio_ready("start");
};

auto transcribe_audio = [](const audio_recorded& e, VoiceControlContext& ctx) {
    // Call STT worker
    ctx.on_audio_ready(e.wav_path);
};

auto parse_intent = [](const text_transcribed& e, VoiceControlContext& ctx) {
    ctx.last_transcription = e.text;
    // NLP processing here
    ctx.on_intent_recognized(e.text);
};

auto execute_command = [](const intent_parsed& e, VoiceControlContext& ctx) {
    // Call hardware workers
    // ctx.on_command_execute(e.tool, e.args);
};

auto prepare_response = [](const command_executed& e, VoiceControlContext& ctx) {
    ctx.pending_response = e.result;
    ctx.on_response_ready(e.result);
};

auto speak_response = [](const response_ready& e, VoiceControlContext& ctx) {
    ctx.on_response_ready(e.text);
};

// FSM Definition
struct voice_control {
    auto operator()() const {
        using namespace sml;

        return make_transition_table(
            *idle + event<wake_word> [has_wake_word] / start_recording = listening,

            listening + event<audio_recorded> / transcribe_audio = processing,

            processing + event<text_transcribed> / parse_intent = processing,
            processing + event<intent_parsed> / execute_command = processing,
            processing + event<command_executed> / prepare_response = speaking,

            speaking + event<response_ready> / speak_response = speaking,
            speaking + event<playback_finished> = idle,

            *error_state + event<error_occurred> = idle
        );
    }
};

class VoiceControlFSM {
public:
    VoiceControlFSM(VoiceControlContext& ctx) : sm_(ctx) {}

    // Process events
    template<typename Event>
    void process_event(const Event& event) {
        sm_.process_event(event);
    }

    // Check current state
    template<typename State>
    bool is_in_state() const {
        return sm_.is(State{});
    }

private:
    sml::sm<voice_control> sm_;
};