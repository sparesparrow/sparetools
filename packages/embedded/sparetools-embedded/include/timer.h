#pragma once

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Simple timer utility for embedded systems
 */
typedef struct {
    uint32_t start_time;
    uint32_t timeout_ms;
    bool active;
} timer_t;

/**
 * @brief Initialize a timer
 * @param timer Timer instance
 * @param timeout_ms Timeout in milliseconds
 */
void timer_init(timer_t* timer, uint32_t timeout_ms);

/**
 * @brief Start the timer
 * @param timer Timer instance
 */
void timer_start(timer_t* timer);

/**
 * @brief Stop the timer
 * @param timer Timer instance
 */
void timer_stop(timer_t* timer);

/**
 * @brief Reset the timer
 * @param timer Timer instance
 */
void timer_reset(timer_t* timer);

/**
 * @brief Check if timer has expired
 * @param timer Timer instance
 * @param current_time Current time in milliseconds
 * @return true if timer has expired
 */
bool timer_expired(timer_t* timer, uint32_t current_time);

/**
 * @brief Get remaining time
 * @param timer Timer instance
 * @param current_time Current time in milliseconds
 * @return remaining time in milliseconds, 0 if expired
 */
uint32_t timer_remaining(timer_t* timer, uint32_t current_time);

/**
 * @brief Get elapsed time since timer start
 * @param timer Timer instance
 * @param current_time Current time in milliseconds
 * @return elapsed time in milliseconds
 */
uint32_t timer_elapsed(timer_t* timer, uint32_t current_time);

#ifdef __cplusplus
}
#endif