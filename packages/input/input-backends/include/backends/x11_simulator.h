#pragma once

#include "input_simulator.h"

namespace gamepad_mapper {

class X11Simulator : public InputSimulator {
public:
    X11Simulator();
    ~X11Simulator() override;

    bool initialize() override;
    void cleanup() override;

    void send_key_press(int key_code) override;
    void send_key_release(int key_code) override;
    void send_mouse_click(MouseButton button) override;
    void send_mouse_move(float delta_x, float delta_y) override;
    void send_mouse_scroll(int delta) override;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace gamepad_mapper