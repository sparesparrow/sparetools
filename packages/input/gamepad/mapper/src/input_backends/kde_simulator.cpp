#include "backends/kde_simulator.h"
#include <dbus/dbus.h>
#include <iostream>
#include <cstring>
#include <unistd.h>
#include <vector>
#include <map>

namespace gamepad_mapper {

class KDESimulator::Impl {
public:
    Impl() : dbus_connection_(nullptr) {}
    ~Impl() { cleanup(); }

    bool initialize() {
        // Initialize DBus connection
        DBusError error;
        dbus_error_init(&error);

        dbus_connection_ = dbus_bus_get(DBUS_BUS_SESSION, &error);
        if (dbus_error_is_set(&error)) {
            std::cerr << "Failed to connect to DBus: " << error.message << std::endl;
            dbus_error_free(&error);
            return false;
        }

        if (!dbus_connection_) {
            std::cerr << "Failed to get DBus connection" << std::endl;
            return false;
        }

        // Test KWin DBus interface
        if (!test_kwin_interface()) {
            std::cerr << "KWin DBus interface not available" << std::endl;
            cleanup();
            return false;
        }

        std::cout << "KDE simulator initialized successfully" << std::endl;
        return true;
    }

    void cleanup() {
        if (dbus_connection_) {
            dbus_connection_unref(dbus_connection_);
            dbus_connection_ = nullptr;
        }
    }

    void send_key_press(int key_code) {
        if (!dbus_connection_) return;

        // Convert Linux key code to Qt key code and send via KWin DBus
        int qt_key = linux_to_qt_key(key_code);
        if (qt_key == 0) return;

        send_dbus_key_event(qt_key, true);
    }

    void send_key_release(int key_code) {
        if (!dbus_connection_) return;

        int qt_key = linux_to_qt_key(key_code);
        if (qt_key == 0) return;

        send_dbus_key_event(qt_key, false);
    }

    void send_mouse_click(MouseButton button) {
        if (!dbus_connection_) return;

        // Send mouse click via KWin DBus
        int button_code = mouse_button_to_qt(button);
        send_dbus_mouse_click(button_code);
    }

    void send_mouse_move(float delta_x, float delta_y) {
        if (!dbus_connection_) return;

        // Send relative mouse movement via KWin DBus
        send_dbus_mouse_move(static_cast<int>(delta_x), static_cast<int>(delta_y));
    }

    void send_mouse_scroll(int delta) {
        if (!dbus_connection_) return;

        // Send mouse wheel event via KWin DBus
        send_dbus_mouse_scroll(delta);
    }

private:
    bool test_kwin_interface() {
        DBusMessage* msg = dbus_message_new_method_call(
            "org.kde.KWin",
            "/KWin",
            "org.freedesktop.DBus.Introspectable",
            "Introspect"
        );

        if (!msg) return false;

        DBusMessage* reply = dbus_connection_send_with_reply_and_block(
            dbus_connection_, msg, 1000, nullptr
        );

        dbus_message_unref(msg);

        if (reply) {
            dbus_message_unref(reply);
            return true;
        }

        return false;
    }

    void send_dbus_key_event(int qt_key, bool press) {
        DBusMessage* msg = dbus_message_new_method_call(
            "org.kde.KWin",
            "/KWin",
            "org.kde.KWin",
            "sendKeyEvent"
        );

        if (!msg) return;

        // Add parameters: key code, pressed state
        dbus_message_append_args(msg,
            DBUS_TYPE_INT32, &qt_key,
            DBUS_TYPE_BOOLEAN, &press,
            DBUS_TYPE_INVALID
        );

        dbus_connection_send(dbus_connection_, msg, nullptr);
        dbus_message_unref(msg);
    }

    void send_dbus_mouse_click(int button) {
        DBusMessage* msg = dbus_message_new_method_call(
            "org.kde.KWin",
            "/KWin",
            "org.kde.KWin",
            "sendMouseEvent"
        );

        if (!msg) return;

        // Parameters: x, y, button, pressed
        int x = 0, y = 0;
        dbus_bool_t pressed = TRUE;

        dbus_message_append_args(msg,
            DBUS_TYPE_INT32, &x,
            DBUS_TYPE_INT32, &y,
            DBUS_TYPE_INT32, &button,
            DBUS_TYPE_BOOLEAN, &pressed,
            DBUS_TYPE_INVALID
        );

        dbus_connection_send(dbus_connection_, msg, nullptr);
        dbus_message_unref(msg);

        // Send release immediately
        pressed = FALSE;
        msg = dbus_message_new_method_call(
            "org.kde.KWin",
            "/KWin",
            "org.kde.KWin",
            "sendMouseEvent"
        );

        if (msg) {
            dbus_message_append_args(msg,
                DBUS_TYPE_INT32, &x,
                DBUS_TYPE_INT32, &y,
                DBUS_TYPE_INT32, &button,
                DBUS_TYPE_BOOLEAN, &pressed,
                DBUS_TYPE_INVALID
            );

            dbus_connection_send(dbus_connection_, msg, nullptr);
            dbus_message_unref(msg);
        }
    }

    void send_dbus_mouse_move(int delta_x, int delta_y) {
        DBusMessage* msg = dbus_message_new_method_call(
            "org.kde.KWin",
            "/KWin",
            "org.kde.KWin",
            "sendMouseMoveEvent"
        );

        if (!msg) return;

        dbus_message_append_args(msg,
            DBUS_TYPE_INT32, &delta_x,
            DBUS_TYPE_INT32, &delta_y,
            DBUS_TYPE_INVALID
        );

        dbus_connection_send(dbus_connection_, msg, nullptr);
        dbus_message_unref(msg);
    }

    void send_dbus_mouse_scroll(int delta) {
        DBusMessage* msg = dbus_message_new_method_call(
            "org.kde.KWin",
            "/KWin",
            "org.kde.KWin",
            "sendMouseWheelEvent"
        );

        if (!msg) return;

        // Convert to Qt wheel delta (120 units per notch)
        int qt_delta = delta * 120;

        dbus_message_append_args(msg,
            DBUS_TYPE_INT32, &qt_delta,
            DBUS_TYPE_INVALID
        );

        dbus_connection_send(dbus_connection_, msg, nullptr);
        dbus_message_unref(msg);
    }

    int linux_to_qt_key(int linux_key) const {
        // Mapping from Linux key codes to Qt key codes
        static const std::map<int, int> key_map = {
            {KEY_ESC, 0x01000000}, // Qt::Key_Escape
            {KEY_1, 0x31}, {KEY_2, 0x32}, {KEY_3, 0x33}, {KEY_4, 0x34}, {KEY_5, 0x35},
            {KEY_Q, 0x51}, {KEY_W, 0x57}, {KEY_E, 0x45}, {KEY_R, 0x52}, {KEY_T, 0x54},
            {KEY_A, 0x41}, {KEY_S, 0x53}, {KEY_D, 0x44}, {KEY_F, 0x46}, {KEY_G, 0x47},
            {KEY_Z, 0x5a}, {KEY_X, 0x58}, {KEY_C, 0x43}, {KEY_V, 0x56}, {KEY_B, 0x42},
            {KEY_LEFTCTRL, 0x01000021}, // Qt::Key_Control
            {KEY_LEFTALT, 0x01000023},   // Qt::Key_Alt
            {KEY_LEFTSHIFT, 0x01000020}, // Qt::Key_Shift
            {KEY_TAB, 0x01000001},       // Qt::Key_Tab
            {KEY_SPACE, 0x20},           // Qt::Key_Space
            {KEY_ENTER, 0x01000005},     // Qt::Key_Return
            {KEY_BACKSPACE, 0x01000003}, // Qt::Key_Backspace
            {KEY_UP, 0x01000013},        // Qt::Key_Up
            {KEY_DOWN, 0x01000015},      // Qt::Key_Down
            {KEY_LEFT, 0x01000012},      // Qt::Key_Left
            {KEY_RIGHT, 0x01000014},     // Qt::Key_Right
        };

        auto it = key_map.find(linux_key);
        return it != key_map.end() ? it->second : 0;
    }

    int mouse_button_to_qt(MouseButton button) const {
        switch (button) {
            case MouseButton::LEFT: return 1;
            case MouseButton::MIDDLE: return 4;
            case MouseButton::RIGHT: return 2;
            default: return 1;
        }
    }

    DBusConnection* dbus_connection_;
};

// Public interface implementation
KDESimulator::KDESimulator() : impl_(std::make_unique<Impl>()) {}
KDESimulator::~KDESimulator() = default;

bool KDESimulator::initialize() { return impl_->initialize(); }
void KDESimulator::cleanup() { impl_->cleanup(); }

void KDESimulator::send_key_press(int key_code) { impl_->send_key_press(key_code); }
void KDESimulator::send_key_release(int key_code) { impl_->send_key_release(key_code); }
void KDESimulator::send_mouse_click(MouseButton button) { impl_->send_mouse_click(button); }
void KDESimulator::send_mouse_move(float delta_x, float delta_y) { impl_->send_mouse_move(delta_x, delta_y); }
void KDESimulator::send_mouse_scroll(int delta) { impl_->send_mouse_scroll(delta); }

} // namespace gamepad_mapper