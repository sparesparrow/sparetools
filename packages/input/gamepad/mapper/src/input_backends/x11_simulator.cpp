#include "backends/x11_simulator.h"
#include <X11/Xlib.h>
#include <X11/extensions/XTest.h>
#include <X11/keysym.h>
#include <linux/input.h>
#include <iostream>
#include <cstring>

namespace gamepad_mapper {

class X11Simulator::Impl {
public:
    Impl() : display_(nullptr) {}
    ~Impl() { cleanup(); }

    bool initialize() {
        display_ = XOpenDisplay(nullptr);
        if (!display_) {
            std::cerr << "Failed to open X11 display" << std::endl;
            return false;
        }

        // Check if XTest extension is available
        int event_base, error_base, major, minor;
        if (!XTestQueryExtension(display_, &event_base, &error_base, &major, &minor)) {
            std::cerr << "XTest extension not available" << std::endl;
            XCloseDisplay(display_);
            display_ = nullptr;
            return false;
        }

        std::cout << "X11 simulator initialized successfully" << std::endl;
        return true;
    }

    void cleanup() {
        if (display_) {
            XCloseDisplay(display_);
            display_ = nullptr;
        }
    }

    void send_key_press(int key_code) {
        if (!display_) return;

        // Convert Linux key code to X11 keysym
        KeySym keysym = linux_to_x11_keysym(key_code);
        if (keysym == NoSymbol) return;

        KeyCode x11_keycode = XKeysymToKeycode(display_, keysym);
        if (x11_keycode == 0) return;

        XTestFakeKeyEvent(display_, x11_keycode, True, CurrentTime);
        XFlush(display_);
    }

    void send_key_release(int key_code) {
        if (!display_) return;

        KeySym keysym = linux_to_x11_keysym(key_code);
        if (keysym == NoSymbol) return;

        KeyCode x11_keycode = XKeysymToKeycode(display_, keysym);
        if (x11_keycode == 0) return;

        XTestFakeKeyEvent(display_, x11_keycode, False, CurrentTime);
        XFlush(display_);
    }

    void send_mouse_click(MouseButton button) {
        if (!display_) return;

        int x11_button = mouse_button_to_x11(button);
        XTestFakeButtonEvent(display_, x11_button, True, CurrentTime);
        XFlush(display_);

        // Release immediately for click
        XTestFakeButtonEvent(display_, x11_button, False, CurrentTime);
        XFlush(display_);
    }

    void send_mouse_move(float delta_x, float delta_y) {
        if (!display_) return;

        // Get current mouse position
        Window root, child;
        int root_x, root_y, win_x, win_y;
        unsigned int mask;

        if (XQueryPointer(display_, DefaultRootWindow(display_),
                         &root, &child, &root_x, &root_y, &win_x, &win_y, &mask)) {
            int new_x = root_x + static_cast<int>(delta_x);
            int new_y = root_y + static_cast<int>(delta_y);

            XWarpPointer(display_, None, DefaultRootWindow(display_),
                        0, 0, 0, 0, new_x, new_y);
            XFlush(display_);
        }
    }

    void send_mouse_scroll(int delta) {
        if (!display_) return;

        // X11 scroll is button 4 (up) and 5 (down)
        int button = (delta > 0) ? 4 : 5;
        XTestFakeButtonEvent(display_, button, True, CurrentTime);
        XFlush(display_);
        XTestFakeButtonEvent(display_, button, False, CurrentTime);
        XFlush(display_);
    }

private:
    KeySym linux_to_x11_keysym(int linux_key) const {
        switch (linux_key) {
            case KEY_ESC: return XK_Escape;
            case KEY_1: return XK_1;
            case KEY_2: return XK_2;
            case KEY_3: return XK_3;
            case KEY_4: return XK_4;
            case KEY_5: return XK_5;
            case KEY_Q: return XK_q;
            case KEY_W: return XK_w;
            case KEY_E: return XK_e;
            case KEY_R: return XK_r;
            case KEY_T: return XK_t;
            case KEY_A: return XK_a;
            case KEY_S: return XK_s;
            case KEY_D: return XK_d;
            case KEY_F: return XK_f;
            case KEY_G: return XK_g;
            case KEY_Z: return XK_z;
            case KEY_X: return XK_x;
            case KEY_C: return XK_c;
            case KEY_V: return XK_v;
            case KEY_B: return XK_b;
            case KEY_LEFTCTRL: return XK_Control_L;
            case KEY_LEFTALT: return XK_Alt_L;
            case KEY_LEFTSHIFT: return XK_Shift_L;
            case KEY_TAB: return XK_Tab;
            case KEY_SPACE: return XK_space;
            case KEY_ENTER: return XK_Return;
            case KEY_BACKSPACE: return XK_BackSpace;
            case KEY_UP: return XK_Up;
            case KEY_DOWN: return XK_Down;
            case KEY_LEFT: return XK_Left;
            case KEY_RIGHT: return XK_Right;
            default: return NoSymbol;
        }
    }

    int mouse_button_to_x11(MouseButton button) const {
        switch (button) {
            case MouseButton::LEFT: return 1;
            case MouseButton::MIDDLE: return 2;
            case MouseButton::RIGHT: return 3;
            default: return 1;
        }
    }

    Display* display_;
};

// Public interface implementation
X11Simulator::X11Simulator() : impl_(std::make_unique<Impl>()) {}
X11Simulator::~X11Simulator() = default;

bool X11Simulator::initialize() { return impl_->initialize(); }
void X11Simulator::cleanup() { impl_->cleanup(); }

void X11Simulator::send_key_press(int key_code) { impl_->send_key_press(key_code); }
void X11Simulator::send_key_release(int key_code) { impl_->send_key_release(key_code); }
void X11Simulator::send_mouse_click(MouseButton button) { impl_->send_mouse_click(button); }
void X11Simulator::send_mouse_move(float delta_x, float delta_y) { impl_->send_mouse_move(delta_x, delta_y); }
void X11Simulator::send_mouse_scroll(int delta) { impl_->send_mouse_scroll(delta); }

} // namespace gamepad_mapper