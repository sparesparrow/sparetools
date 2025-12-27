#include "backends/uinput_simulator.h"
#include <linux/uinput.h>
#include <linux/input.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <cstring>
#include <sys/ioctl.h>

namespace gamepad_mapper {

class UInputSimulator::Impl {
public:
    Impl() : uinput_fd_(-1) {}
    ~Impl() { cleanup(); }

    bool initialize() {
        // Open uinput device
        uinput_fd_ = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
        if (uinput_fd_ < 0) {
            std::cerr << "Failed to open /dev/uinput: " << strerror(errno) << std::endl;
            std::cerr << "Make sure uinput kernel module is loaded and permissions are correct" << std::endl;
            return false;
        }

        // Configure device capabilities
        if (!setup_device_capabilities()) {
            cleanup();
            return false;
        }

        // Create the device
        struct uinput_setup setup;
        memset(&setup, 0, sizeof(setup));
        strcpy(setup.name, "GamepadMapper Virtual Input");
        setup.id.bustype = BUS_VIRTUAL;
        setup.id.vendor = 0x1234;
        setup.id.product = 0x5678;
        setup.id.version = 1;

        if (ioctl(uinput_fd_, UI_DEV_SETUP, &setup) < 0) {
            std::cerr << "UI_DEV_SETUP failed: " << strerror(errno) << std::endl;
            cleanup();
            return false;
        }

        if (ioctl(uinput_fd_, UI_DEV_CREATE) < 0) {
            std::cerr << "UI_DEV_CREATE failed: " << strerror(errno) << std::endl;
            cleanup();
            return false;
        }

        // Give the device time to settle
        usleep(100000); // 100ms

        std::cout << "UInput simulator initialized successfully" << std::endl;
        return true;
    }

    void cleanup() {
        if (uinput_fd_ >= 0) {
            ioctl(uinput_fd_, UI_DEV_DESTROY);
            close(uinput_fd_);
            uinput_fd_ = -1;
        }
    }

    void send_key_press(int key_code) {
        if (uinput_fd_ < 0) return;

        send_input_event(EV_KEY, key_code, 1); // Press
        send_input_event(EV_SYN, SYN_REPORT, 0); // Sync
    }

    void send_key_release(int key_code) {
        if (uinput_fd_ < 0) return;

        send_input_event(EV_KEY, key_code, 0); // Release
        send_input_event(EV_SYN, SYN_REPORT, 0); // Sync
    }

    void send_mouse_click(MouseButton button) {
        if (uinput_fd_ < 0) return;

        int btn_code = mouse_button_to_uinput(button);

        send_input_event(EV_KEY, btn_code, 1); // Press
        send_input_event(EV_SYN, SYN_REPORT, 0); // Sync

        usleep(10000); // 10ms delay

        send_input_event(EV_KEY, btn_code, 0); // Release
        send_input_event(EV_SYN, SYN_REPORT, 0); // Sync
    }

    void send_mouse_move(float delta_x, float delta_y) {
        if (uinput_fd_ < 0) return;

        // Send relative mouse movement
        send_input_event(EV_REL, REL_X, static_cast<int>(delta_x));
        send_input_event(EV_REL, REL_Y, static_cast<int>(delta_y));
        send_input_event(EV_SYN, SYN_REPORT, 0);
    }

    void send_mouse_scroll(int delta) {
        if (uinput_fd_ < 0) return;

        // Send vertical scroll wheel
        send_input_event(EV_REL, REL_WHEEL, delta);
        send_input_event(EV_SYN, SYN_REPORT, 0);
    }

private:
    bool setup_device_capabilities() {
        // Enable keyboard events
        if (ioctl(uinput_fd_, UI_SET_EVBIT, EV_KEY) < 0) return false;

        // Enable mouse events
        if (ioctl(uinput_fd_, UI_SET_EVBIT, EV_REL) < 0) return false;

        // Enable mouse relative axes
        if (ioctl(uinput_fd_, UI_SET_RELBIT, REL_X) < 0) return false;
        if (ioctl(uinput_fd_, UI_SET_RELBIT, REL_Y) < 0) return false;
        if (ioctl(uinput_fd_, UI_SET_RELBIT, REL_WHEEL) < 0) return false;

        // Enable common keyboard keys
        const int keys[] = {
            KEY_ESC, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5,
            KEY_Q, KEY_W, KEY_E, KEY_R, KEY_T,
            KEY_A, KEY_S, KEY_D, KEY_F, KEY_G,
            KEY_Z, KEY_X, KEY_C, KEY_V, KEY_B,
            KEY_LEFTCTRL, KEY_LEFTALT, KEY_LEFTSHIFT,
            KEY_TAB, KEY_SPACE, KEY_ENTER, KEY_BACKSPACE,
            KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT,
            BTN_LEFT, BTN_RIGHT, BTN_MIDDLE
        };

        for (int key : keys) {
            if (ioctl(uinput_fd_, UI_SET_KEYBIT, key) < 0) {
                std::cerr << "Failed to set keybit for key " << key << std::endl;
                return false;
            }
        }

        return true;
    }

    void send_input_event(unsigned short type, unsigned short code, int value) {
        struct input_event event;
        memset(&event, 0, sizeof(event));

        event.type = type;
        event.code = code;
        event.value = value;
        event.time.tv_sec = 0;
        event.time.tv_usec = 0;

        if (write(uinput_fd_, &event, sizeof(event)) < 0) {
            std::cerr << "Failed to write input event: " << strerror(errno) << std::endl;
        }
    }

    int mouse_button_to_uinput(MouseButton button) const {
        switch (button) {
            case MouseButton::LEFT: return BTN_LEFT;
            case MouseButton::MIDDLE: return BTN_MIDDLE;
            case MouseButton::RIGHT: return BTN_RIGHT;
            default: return BTN_LEFT;
        }
    }

    int uinput_fd_;
};

// Public interface implementation
UInputSimulator::UInputSimulator() : impl_(std::make_unique<Impl>()) {}
UInputSimulator::~UInputSimulator() = default;

bool UInputSimulator::initialize() { return impl_->initialize(); }
void UInputSimulator::cleanup() { impl_->cleanup(); }

void UInputSimulator::send_key_press(int key_code) { impl_->send_key_press(key_code); }
void UInputSimulator::send_key_release(int key_code) { impl_->send_key_release(key_code); }
void UInputSimulator::send_mouse_click(MouseButton button) { impl_->send_mouse_click(button); }
void UInputSimulator::send_mouse_move(float delta_x, float delta_y) { impl_->send_mouse_move(delta_x, delta_y); }
void UInputSimulator::send_mouse_scroll(int delta) { impl_->send_mouse_scroll(delta); }

} // namespace gamepad_mapper