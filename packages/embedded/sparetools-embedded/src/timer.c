#include "timer.h"

void timer_init(timer_t* timer, uint32_t timeout_ms) {
    if (!timer) {
        return;
    }

    timer->start_time = 0;
    timer->timeout_ms = timeout_ms;
    timer->active = false;
}

void timer_start(timer_t* timer) {
    if (!timer) {
        return;
    }

    timer->active = true;
    // Note: In a real embedded system, you'd get current time from a system timer
    // For now, we'll assume the caller provides current_time to timer functions
}

void timer_stop(timer_t* timer) {
    if (!timer) {
        return;
    }

    timer->active = false;
}

void timer_reset(timer_t* timer) {
    if (!timer) {
        return;
    }

    timer->start_time = 0;
    timer->active = false;
}

bool timer_expired(timer_t* timer, uint32_t current_time) {
    if (!timer || !timer->active) {
        return false;
    }

    return (current_time - timer->start_time) >= timer->timeout_ms;
}

uint32_t timer_remaining(timer_t* timer, uint32_t current_time) {
    if (!timer || !timer->active) {
        return 0;
    }

    uint32_t elapsed = current_time - timer->start_time;
    if (elapsed >= timer->timeout_ms) {
        return 0;
    }

    return timer->timeout_ms - elapsed;
}

uint32_t timer_elapsed(timer_t* timer, uint32_t current_time) {
    if (!timer || !timer->active) {
        return 0;
    }

    return current_time - timer->start_time;
}



