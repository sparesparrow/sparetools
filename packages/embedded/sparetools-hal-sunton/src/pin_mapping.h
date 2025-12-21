#ifndef SUNTON_PIN_MAPPING_H
#define SUNTON_PIN_MAPPING_H

/**
 * @file pin_mapping.h
 * @brief Pin mappings for Sunton ESP32-2432S028Rv3 display board
 *
 * This file defines the pin connections for the Sunton ESP32-2432S028Rv3
 * TFT display module with resistive touch screen.
 */

#ifdef __cplusplus
extern "C" {
#endif

// TFT Display Pins (ILI9341)
#define TFT_MISO    19  ///< SPI MISO pin
#define TFT_MOSI    23  ///< SPI MOSI pin
#define TFT_SCLK    18  ///< SPI Clock pin
#define TFT_CS      15  ///< Chip Select pin
#define TFT_DC       2  ///< Data/Command pin
#define TFT_RST      4  ///< Reset pin
#define TFT_BL      32  ///< Backlight control pin

// Touch Screen Pins (XPT2046)
#define TOUCH_CS    33  ///< Touch controller chip select
#define TOUCH_IRQ   36  ///< Touch interrupt pin (optional)

// Power and Control
#define POWER_LED   12  ///< Power LED indicator
#define USER_BUTTON  0  ///< User button (BOOT button)

// I2C Pins (available for external sensors)
#define I2C_SDA     21  ///< I2C SDA pin
#define I2C_SCL     22  ///< I2C SCL pin

// UART Pins (for debugging)
#define UART_TX     17  ///< UART TX pin
#define UART_RX     16  ///< UART RX pin

// ADC Pins (available for sensors)
#define ADC1_CH0    36  ///< ADC1 Channel 0 (VP)
#define ADC1_CH3    39  ///< ADC1 Channel 3 (VN)
#define ADC1_CH4    32  ///< ADC1 Channel 4 (BACKLIGHT, shared)
#define ADC1_CH5    33  ///< ADC1 Channel 5 (TOUCH_CS, shared)
#define ADC1_CH6    34  ///< ADC1 Channel 6
#define ADC1_CH7    35  ///< ADC1 Channel 7

// PWM Capable Pins
#define PWM_PINS    {12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33}

// SPI Pins (HSPI - Hardware SPI)
#define HSPI_MISO   19
#define HSPI_MOSI   23
#define HSPI_SCLK   18
#define HSPI_CS     15

// SPI Pins (VSPI - Virtual SPI, available)
#define VSPI_MISO   25
#define VSPI_MOSI   26
#define VSPI_SCLK   27
#define VSPI_CS     5

// Display Configuration
#define DISPLAY_WIDTH   240
#define DISPLAY_HEIGHT  320
#define DISPLAY_ROTATION 0   // 0=Portrait, 1=Landscape, 2=Portrait inverted, 3=Landscape inverted

// Touch Configuration
#define TOUCH_WIDTH     240
#define TOUCH_HEIGHT    320
#define TOUCH_ROTATION  0

// Backlight Configuration
#define BACKLIGHT_FREQUENCY  5000  // PWM frequency in Hz
#define BACKLIGHT_RESOLUTION 8     // PWM resolution in bits
#define BACKLIGHT_CHANNEL    0     // PWM channel

#ifdef __cplusplus
}
#endif

#endif // SUNTON_PIN_MAPPING_H