#include "voice_control_fsm.hpp"
#include <iostream>

// VoiceControlFSM implementation
VoiceControlFSM::VoiceControlFSM(VoiceControlContext& ctx) : sm_(ctx) {
    // Constructor - state machine is initialized with the context
}

template<typename Event>
void VoiceControlFSM::process_event(const Event& event) {
    sm_.process_event(event);
}

// Explicit template instantiations for the events we support
template void VoiceControlFSM::process_event<wake_word>(const wake_word& event);
template void VoiceControlFSM::process_event<audio_recorded>(const audio_recorded& event);
template void VoiceControlFSM::process_event<text_transcribed>(const text_transcribed& event);
template void VoiceControlFSM::process_event<intent_parsed>(const intent_parsed& event);
template void VoiceControlFSM::process_event<command_executed>(const command_executed& event);
template void VoiceControlFSM::process_event<response_ready>(const response_ready& event);
template void VoiceControlFSM::process_event<playback_finished>(const playback_finished& event);
template void VoiceControlFSM::process_event<error_occurred>(const error_occurred& event);

template<typename State>
bool VoiceControlFSM::is_in_state() const {
    return sm_.is(State{});
}

// Explicit template instantiations for state checking
template bool VoiceControlFSM::is_in_state<decltype(idle)>() const;
template bool VoiceControlFSM::is_in_state<decltype(listening)>() const;
template bool VoiceControlFSM::is_in_state<decltype(processing)>() const;
template bool VoiceControlFSM::is_in_state<decltype(speaking)>() const;
template bool VoiceControlFSM::is_in_state<decltype(error_state)>() const;