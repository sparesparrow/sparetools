#pragma once

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Thread-safe ring buffer implementation for embedded systems
 */
typedef struct {
    uint8_t* buffer;
    size_t size;
    size_t head;
    size_t tail;
    bool full;
} ring_buffer_t;

/**
 * @brief Initialize a ring buffer
 * @param rb Ring buffer instance
 * @param buffer Buffer array
 * @param size Buffer size (must be power of 2 for optimal performance)
 * @return true on success, false on failure
 */
bool ring_buffer_init(ring_buffer_t* rb, uint8_t* buffer, size_t size);

/**
 * @brief Check if ring buffer is empty
 * @param rb Ring buffer instance
 * @return true if empty
 */
bool ring_buffer_is_empty(const ring_buffer_t* rb);

/**
 * @brief Check if ring buffer is full
 * @param rb Ring buffer instance
 * @return true if full
 */
bool ring_buffer_is_full(const ring_buffer_t* rb);

/**
 * @brief Get number of bytes available for reading
 * @param rb Ring buffer instance
 * @return number of bytes available
 */
size_t ring_buffer_available(const ring_buffer_t* rb);

/**
 * @brief Put a byte into the ring buffer
 * @param rb Ring buffer instance
 * @param data Byte to put
 * @return true on success, false if buffer is full
 */
bool ring_buffer_put(ring_buffer_t* rb, uint8_t data);

/**
 * @brief Get a byte from the ring buffer
 * @param rb Ring buffer instance
 * @param data Pointer to store retrieved byte
 * @return true on success, false if buffer is empty
 */
bool ring_buffer_get(ring_buffer_t* rb, uint8_t* data);

/**
 * @brief Put multiple bytes into the ring buffer
 * @param rb Ring buffer instance
 * @param data Buffer with data to put
 * @param len Number of bytes to put
 * @return number of bytes actually put
 */
size_t ring_buffer_put_bulk(ring_buffer_t* rb, const uint8_t* data, size_t len);

/**
 * @brief Get multiple bytes from the ring buffer
 * @param rb Ring buffer instance
 * @param data Buffer to store retrieved data
 * @param len Number of bytes to get
 * @return number of bytes actually retrieved
 */
size_t ring_buffer_get_bulk(ring_buffer_t* rb, uint8_t* data, size_t len);

/**
 * @brief Clear the ring buffer
 * @param rb Ring buffer instance
 */
void ring_buffer_clear(ring_buffer_t* rb);

#ifdef __cplusplus
}
#endif