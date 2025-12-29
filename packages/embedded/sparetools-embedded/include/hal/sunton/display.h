#ifndef HAL_SUNTON_DISPLAY_H
#define HAL_SUNTON_DISPLAY_H

/**
 * @file display.h
 * @brief Hardware abstraction layer for Sunton ESP32-2432S028Rv3 display
 *
 * This header provides the interface for display operations on the Sunton
 * ESP32-2432S028Rv3 board with ILI9341 TFT controller and XPT2046 touch.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifdef WITH_LVGL
// Forward declarations for LVGL integration
struct _lv_disp_drv_t;
struct _lv_indev_drv_t;
typedef struct _lv_disp_drv_t lv_disp_drv_t;
typedef struct _lv_indev_drv_t lv_indev_drv_t;
#endif

/**
 * @brief Display configuration structure
 */
typedef struct {
    uint16_t width;           ///< Display width in pixels
    uint16_t height;          ///< Display height in pixels
    uint8_t rotation;         ///< Display rotation (0-3)
    bool backlight_enabled;   ///< Backlight control
    uint8_t brightness;       ///< Backlight brightness (0-255)
} sunton_display_config_t;

/**
 * @brief Touch configuration structure
 */
typedef struct {
    uint16_t width;           ///< Touch panel width
    uint16_t height;          ///< Touch panel height
    uint8_t rotation;         ///< Touch rotation (0-3)
    bool enabled;             ///< Touch enable/disable
} sunton_touch_config_t;

/**
 * @brief Display driver handle
 */
typedef struct sunton_display_handle_t sunton_display_handle_t;

/**
 * @brief Initialize the Sunton display hardware
 *
 * This function initializes the TFT display and backlight control.
 *
 * @param config Pointer to display configuration (can be NULL for defaults)
 * @return Display handle on success, NULL on failure
 */
sunton_display_handle_t* sunton_display_init(const sunton_display_config_t* config);

/**
 * @brief Deinitialize the display hardware
 *
 * @param handle Display handle to deinitialize
 */
void sunton_display_deinit(sunton_display_handle_t* handle);

/**
 * @brief Set display backlight brightness
 *
 * @param handle Display handle
 * @param brightness Brightness level (0-255, 0 = off, 255 = max)
 */
void sunton_display_set_brightness(sunton_display_handle_t* handle, uint8_t brightness);

/**
 * @brief Enable or disable display backlight
 *
 * @param handle Display handle
 * @param enabled True to enable backlight, false to disable
 */
void sunton_display_enable_backlight(sunton_display_handle_t* handle, bool enabled);

#ifdef WITH_LVGL
/**
 * @brief Get LVGL display driver for integration
 *
 * @param handle Display handle
 * @return Pointer to LVGL display driver structure
 */
lv_disp_drv_t* sunton_display_get_lvgl_driver(sunton_display_handle_t* handle);
#endif

/**
 * @brief Initialize touch controller
 *
 * @param config Pointer to touch configuration (can be NULL for defaults)
 * @return True on success, false on failure
 */
bool sunton_touch_init(const sunton_touch_config_t* config);

/**
 * @brief Deinitialize touch controller
 */
void sunton_touch_deinit(void);

#ifdef WITH_LVGL
/**
 * @brief Get LVGL touch input driver for integration
 *
 * @return Pointer to LVGL input driver structure
 */
lv_indev_drv_t* sunton_touch_get_lvgl_driver(void);
#endif

/**
 * @brief Read touch coordinates
 *
 * @param x Pointer to store X coordinate
 * @param y Pointer to store Y coordinate
 * @param pressed Pointer to store touch state (true if pressed)
 * @return True if coordinates are valid, false otherwise
 */
bool sunton_touch_read(uint16_t* x, uint16_t* y, bool* pressed);

/**
 * @brief Calibrate touch screen
 *
 * This function performs touch screen calibration and stores calibration data.
 *
 * @return True on successful calibration, false on failure
 */
bool sunton_touch_calibrate(void);

/**
 * @brief Check if display hardware is ready
 *
 * @param handle Display handle
 * @return True if hardware is ready, false otherwise
 */
bool sunton_display_is_ready(sunton_display_handle_t* handle);

/**
 * @brief Get display information
 *
 * @param handle Display handle
 * @param width Pointer to store display width
 * @param height Pointer to store display height
 */
void sunton_display_get_info(sunton_display_handle_t* handle, uint16_t* width, uint16_t* height);

#ifdef WITH_LVGL
/**
 * @brief Flush display buffer (LVGL callback)
 *
 * @param drv LVGL display driver
 * @param area Area to flush
 * @param color_p Color buffer
 */
void sunton_display_flush_cb(lv_disp_drv_t* drv, const lv_area_t* area, lv_color_t* color_p);

/**
 * @brief Touch read callback for LVGL
 *
 * @param drv LVGL input driver
 * @param data Input data structure
 */
void sunton_touch_read_cb(lv_indev_drv_t* drv, lv_indev_data_t* data);
#endif

#ifdef __cplusplus
}
#endif

#endif // HAL_SUNTON_DISPLAY_H