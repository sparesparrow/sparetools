#include "ring_buffer.h"
#include <string.h>
#include <assert.h>

bool ring_buffer_init(ring_buffer_t* rb, uint8_t* buffer, size_t size) {
    if (!rb || !buffer || size == 0) {
        return false;
    }

    // Size should be power of 2 for optimal performance
    rb->buffer = buffer;
    rb->size = size;
    rb->head = 0;
    rb->tail = 0;
    rb->full = false;

    return true;
}

bool ring_buffer_is_empty(const ring_buffer_t* rb) {
    return (!rb->full && (rb->head == rb->tail));
}

bool ring_buffer_is_full(const ring_buffer_t* rb) {
    return rb->full;
}

size_t ring_buffer_available(const ring_buffer_t* rb) {
    if (rb->full) {
        return rb->size;
    }

    if (rb->head >= rb->tail) {
        return rb->head - rb->tail;
    } else {
        return rb->size + rb->head - rb->tail;
    }
}

bool ring_buffer_put(ring_buffer_t* rb, uint8_t data) {
    if (ring_buffer_is_full(rb)) {
        return false;
    }

    rb->buffer[rb->head] = data;
    rb->head = (rb->head + 1) % rb->size;

    if (rb->head == rb->tail) {
        rb->full = true;
    }

    return true;
}

bool ring_buffer_get(ring_buffer_t* rb, uint8_t* data) {
    if (ring_buffer_is_empty(rb)) {
        return false;
    }

    *data = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) % rb->size;
    rb->full = false;

    return true;
}

size_t ring_buffer_put_bulk(ring_buffer_t* rb, const uint8_t* data, size_t len) {
    size_t available_space = rb->size - ring_buffer_available(rb);
    size_t to_put = (len < available_space) ? len : available_space;

    for (size_t i = 0; i < to_put; i++) {
        ring_buffer_put(rb, data[i]);
    }

    return to_put;
}

size_t ring_buffer_get_bulk(ring_buffer_t* rb, uint8_t* data, size_t len) {
    size_t available = ring_buffer_available(rb);
    size_t to_get = (len < available) ? len : available;

    for (size_t i = 0; i < to_get; i++) {
        ring_buffer_get(rb, &data[i]);
    }

    return to_get;
}

void ring_buffer_clear(ring_buffer_t* rb) {
    rb->head = 0;
    rb->tail = 0;
    rb->full = false;
}




