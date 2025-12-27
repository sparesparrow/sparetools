#include "backends/sdl2_simulator.h"
#include <SDL2/SDL.h>
#include <linux/input.h>
#include <iostream>
#include <cstring>

namespace gamepad_mapper {

class SDL2Simulator::Impl {
public:
    Impl() { SDL_memset(&current_mouse_state_, 0, sizeof(current_mouse_state_)); }
    ~Impl() { cleanup(); }

    bool initialize() {
        if (SDL_Init(SDL_INIT_EVENTS) < 0) {
            std::cerr << "Failed to initialize SDL: " << SDL_GetError() << std::endl;
            return false;
        }

        // Get current mouse state
        SDL_GetGlobalMouseState(&current_mouse_state_.x, &current_mouse_state_.y);

        std::cout << "SDL2 simulator initialized successfully" << std::endl;
        return true;
    }

    void cleanup() {
        SDL_Quit();
    }

    void send_key_press(int key_code) {
        SDL_Event event;
        SDL_memset(&event, 0, sizeof(event));

        event.type = SDL_KEYDOWN;
        event.key.timestamp = SDL_GetTicks();
        event.key.keysym.sym = linux_to_sdl_key(key_code);
        event.key.keysym.mod = KMOD_NONE;
        event.key.state = SDL_PRESSED;
        event.key.repeat = 0;

        SDL_PushEvent(&event);
    }

    void send_key_release(int key_code) {
        SDL_Event event;
        SDL_memset(&event, 0, sizeof(event));

        event.type = SDL_KEYUP;
        event.key.timestamp = SDL_GetTicks();
        event.key.keysym.sym = linux_to_sdl_key(key_code);
        event.key.keysym.mod = KMOD_NONE;
        event.key.state = SDL_RELEASED;
        event.key.repeat = 0;

        SDL_PushEvent(&event);
    }

    void send_mouse_click(MouseButton button) {
        Uint32 sdl_button = mouse_button_to_sdl(button);

        // Mouse down event
        SDL_Event down_event;
        SDL_memset(&down_event, 0, sizeof(down_event));

        down_event.type = SDL_MOUSEBUTTONDOWN;
        down_event.button.timestamp = SDL_GetTicks();
        down_event.button.windowID = 0;
        down_event.button.which = 0;
        down_event.button.button = sdl_button;
        down_event.button.state = SDL_PRESSED;
        down_event.button.clicks = 1;
        down_event.button.x = current_mouse_state_.x;
        down_event.button.y = current_mouse_state_.y;

        SDL_PushEvent(&down_event);

        // Mouse up event (immediate release for click)
        SDL_Event up_event = down_event;
        up_event.type = SDL_MOUSEBUTTONUP;
        up_event.button.state = SDL_RELEASED;

        SDL_PushEvent(&up_event);
    }

    void send_mouse_move(float delta_x, float delta_y) {
        int new_x = current_mouse_state_.x + static_cast<int>(delta_x);
        int new_y = current_mouse_state_.y + static_cast<int>(delta_y);

        // Clamp to reasonable bounds (assuming 1920x1080 as fallback)
        new_x = SDL_max(0, SDL_min(new_x, 1920));
        new_y = SDL_max(0, SDL_min(new_y, 1080));

        // Update mouse position
        SDL_WarpMouseGlobal(new_x, new_y);

        // Send mouse motion event
        SDL_Event event;
        SDL_memset(&event, 0, sizeof(event));

        event.type = SDL_MOUSEMOTION;
        event.motion.timestamp = SDL_GetTicks();
        event.motion.windowID = 0;
        event.motion.which = 0;
        event.motion.state = 0;
        event.motion.x = new_x;
        event.motion.y = new_y;
        event.motion.xrel = static_cast<Sint32>(delta_x);
        event.motion.yrel = static_cast<Sint32>(delta_y);

        SDL_PushEvent(&event);

        current_mouse_state_.x = new_x;
        current_mouse_state_.y = new_y;
    }

    void send_mouse_scroll(int delta) {
        SDL_Event event;
        SDL_memset(&event, 0, sizeof(event));

        event.type = SDL_MOUSEWHEEL;
        event.wheel.timestamp = SDL_GetTicks();
        event.wheel.windowID = 0;
        event.wheel.which = 0;
        event.wheel.x = 0;
        event.wheel.y = delta;
        event.wheel.direction = SDL_MOUSEWHEEL_NORMAL;

        SDL_PushEvent(&event);
    }

private:
    SDL_Keycode linux_to_sdl_key(int linux_key) const {
        switch (linux_key) {
            case KEY_ESC: return SDLK_ESCAPE;
            case KEY_1: return SDLK_1;
            case KEY_2: return SDLK_2;
            case KEY_3: return SDLK_3;
            case KEY_4: return SDLK_4;
            case KEY_5: return SDLK_5;
            case KEY_Q: return SDLK_q;
            case KEY_W: return SDLK_w;
            case KEY_E: return SDLK_e;
            case KEY_R: return SDLK_r;
            case KEY_T: return SDLK_t;
            case KEY_A: return SDLK_a;
            case KEY_S: return SDLK_s;
            case KEY_D: return SDLK_d;
            case KEY_F: return SDLK_f;
            case KEY_G: return SDLK_g;
            case KEY_Z: return SDLK_z;
            case KEY_X: return SDLK_x;
            case KEY_C: return SDLK_c;
            case KEY_V: return SDLK_v;
            case KEY_B: return SDLK_b;
            case KEY_LEFTCTRL: return SDLK_LCTRL;
            case KEY_LEFTALT: return SDLK_LALT;
            case KEY_LEFTSHIFT: return SDLK_LSHIFT;
            case KEY_TAB: return SDLK_TAB;
            case KEY_SPACE: return SDLK_SPACE;
            case KEY_ENTER: return SDLK_RETURN;
            case KEY_BACKSPACE: return SDLK_BACKSPACE;
            case KEY_UP: return SDLK_UP;
            case KEY_DOWN: return SDLK_DOWN;
            case KEY_LEFT: return SDLK_LEFT;
            case KEY_RIGHT: return SDLK_RIGHT;
            default: return SDLK_UNKNOWN;
        }
    }

    Uint32 mouse_button_to_sdl(MouseButton button) const {
        switch (button) {
            case MouseButton::LEFT: return SDL_BUTTON_LEFT;
            case MouseButton::MIDDLE: return SDL_BUTTON_MIDDLE;
            case MouseButton::RIGHT: return SDL_BUTTON_RIGHT;
            default: return SDL_BUTTON_LEFT;
        }
    }

    struct {
        int x, y;
    } current_mouse_state_;
};

// Public interface implementation
SDL2Simulator::SDL2Simulator() : impl_(std::make_unique<Impl>()) {}
SDL2Simulator::~SDL2Simulator() = default;

bool SDL2Simulator::initialize() { return impl_->initialize(); }
void SDL2Simulator::cleanup() { impl_->cleanup(); }

void SDL2Simulator::send_key_press(int key_code) { impl_->send_key_press(key_code); }
void SDL2Simulator::send_key_release(int key_code) { impl_->send_key_release(key_code); }
void SDL2Simulator::send_mouse_click(MouseButton button) { impl_->send_mouse_click(button); }
void SDL2Simulator::send_mouse_move(float delta_x, float delta_y) { impl_->send_mouse_move(delta_x, delta_y); }
void SDL2Simulator::send_mouse_scroll(int delta) { impl_->send_mouse_scroll(delta); }

} // namespace gamepad_mapper