#pragma once

namespace gamepad_mapper {

// Gamepad event structures
struct GamepadEvent {
    enum Type { BUTTON, AXIS } type;

    struct ButtonEvent {
        int code;
        bool pressed;
    } button;

    struct AxisEvent {
        int code;
        int value;  // -32767 to 32767
    } axis;
};

} // namespace gamepad_mapper