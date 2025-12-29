#include "audio_input.h"

#ifdef ESP32
#include <esp_adc_cal.h>
#include <driver/adc.h>

// ADC calibration data (optional, improves accuracy)
static esp_adc_cal_characteristics_t* adc_chars = nullptr;
#endif

AudioInput::AudioInput()
    : adc_pin_(0)
    , initialized_(false)
    , signal_level_(0.0f)
    , max_signal_(0.0f)
    , min_signal_(4095.0f)
    , rms_index_(0)
{
    rms_buffer_.reserve(RMS_BUFFER_SIZE);
    rms_buffer_.resize(RMS_BUFFER_SIZE, 0.0f);
}

AudioInput::~AudioInput() {
#ifdef ESP32
    if (adc_chars) {
        free(adc_chars);
        adc_chars = nullptr;
    }
#endif
}

void AudioInput::begin(uint8_t adc_pin) {
    adc_pin_ = adc_pin;
    
    // Configure ADC
    // ESP32 ADC1 channels: GPIO32-39
    // We'll use analogRead() which handles ADC setup automatically
    // But we can also configure manually for better control
    
    // Set ADC resolution (Arduino API)
    analogReadResolution(ADC_RESOLUTION);
    
    // Set ADC attenuation (0-3.6V range for MAX9814)
    // Use Arduino analogSetAttenuation() if available, otherwise use ESP-IDF directly
    #ifdef ESP32
        // Map pin to ADC channel
        adc1_channel_t channel = ADC1_CHANNEL_MAX;
        if (adc_pin == 32) channel = ADC1_CHANNEL_4;
        else if (adc_pin == 33) channel = ADC1_CHANNEL_5;
        else if (adc_pin == 34) channel = ADC1_CHANNEL_6;
        else if (adc_pin == 35) channel = ADC1_CHANNEL_7;
        else if (adc_pin == 36) channel = ADC1_CHANNEL_0;
        else if (adc_pin == 37) channel = ADC1_CHANNEL_1;
        else if (adc_pin == 38) channel = ADC1_CHANNEL_2;
        else if (adc_pin == 39) channel = ADC1_CHANNEL_3;
        
        if (channel != ADC1_CHANNEL_MAX) {
            // Configure ADC width and attenuation
            adc1_config_width(ADC_WIDTH_BIT_12);
            adc1_config_channel_atten(channel, ADC_ATTENUATION);
            
            // Initialize calibration (optional, for better accuracy)
            if (!adc_chars) {
                adc_chars = (esp_adc_cal_characteristics_t*)calloc(1, sizeof(esp_adc_cal_characteristics_t));
                esp_adc_cal_value_t val_type = esp_adc_cal_characterize(
                    ADC_UNIT_1, 
                    ADC_ATTENUATION, 
                    ADC_WIDTH_BIT_12, 
                    1100,  // Default Vref
                    adc_chars
                );
            }
        }
    #endif
    
    // Reset calibration
    resetCalibration();
    
    initialized_ = true;
    
    #if DEBUG_SERIAL
        DEBUG_PRINTF("[AudioInput] Initialized on pin %d\n", adc_pin_);
    #endif
}

float AudioInput::readSample() {
    if (!initialized_) {
        #if DEBUG_SERIAL
            DEBUG_PRINTLN("[AudioInput] Warning: readSample() called before initialization");
        #endif
        return 0.0f;
    }

    // Read raw ADC value (0-4095 for 12-bit)
    int raw_value = analogRead(adc_pin_);
    
    // Validate ADC reading
    if (raw_value < 0 || raw_value > 4095) {
        #if DEBUG_SERIAL
            DEBUG_PRINTF("[AudioInput] Warning: Invalid ADC reading: %d\n", raw_value);
        #endif
        raw_value = 2048; // Use midpoint as fallback
    }

    // Convert to voltage (0.0-3.6V for ADC_ATTEN_DB_11)
    // For 12-bit ADC with 3.6V max: voltage = (raw / 4095.0) * 3.6
    float voltage = (raw_value / 4095.0f) * 3.6f;

    // Center around 0 (AC coupling - remove DC offset)
    // MAX9814 typically outputs 1.5V DC offset with AC signal
    static float dc_offset = 1.5f;  // Will adapt over time
    float ac_signal = voltage - dc_offset;

    // Update DC offset estimation (slow adaptation)
    dc_offset = dc_offset * 0.999f + voltage * 0.001f;

    // #region agent log
    static unsigned long sampleCount = 0;
    sampleCount++;
    if (sampleCount % 1000 == 0) {  // Log every 1000 samples to avoid spam
        char dataBuf[128];
        snprintf(dataBuf, sizeof(dataBuf), "{\"rawValue\":%d,\"voltage\":%.3f,\"acSignal\":%.3f,\"dcOffset\":%.3f,\"sampleCount\":%lu}",
                 raw_value, voltage, ac_signal, dc_offset, sampleCount);
        // Using external writeLog function - need to declare it
        extern void writeLog(const char*, const char*, const char*, const char*);
        writeLog("audio_input.cpp:readSample", "Audio sample data", "B", dataBuf);
    }
    // #endregion

    // Update signal level tracking
    updateSignalLevel(ac_signal);

    return ac_signal;
}

void AudioInput::updateSignalLevel(float sample) {
    // Add to RMS buffer
    float abs_sample = fabs(sample);
    rms_buffer_[rms_index_] = abs_sample;
    rms_index_ = (rms_index_ + 1) % RMS_BUFFER_SIZE;
    
    // Update peak tracking
    if (abs_sample > max_signal_) {
        max_signal_ = abs_sample;
    }
    if (abs_sample < min_signal_) {
        min_signal_ = abs_sample;
    }
    
    // Calculate RMS signal level
    signal_level_ = calculateRMS();
}

float AudioInput::calculateRMS() const {
    if (rms_buffer_.empty()) {
        return 0.0f;
    }
    
    float sum_squares = 0.0f;
    for (float sample : rms_buffer_) {
        sum_squares += sample * sample;
    }
    
    return sqrt(sum_squares / rms_buffer_.size());
}

float AudioInput::getSignalLevel() const {
    return signal_level_;
}

float AudioInput::getNormalizedLevel() const {
    // Normalize to 0.0-1.0 range
    // Use max_signal_ as reference, but clamp to reasonable range
    float max_ref = max_signal_;
    if (max_ref < 0.01f) {
        max_ref = 0.01f;  // Avoid division by zero
    }
    
    float normalized = signal_level_ / max_ref;
    if (normalized > 1.0f) {
        normalized = 1.0f;
    }
    
    return normalized;
}

bool AudioInput::isInitialized() const {
    return initialized_;
}

void AudioInput::resetCalibration() {
    signal_level_ = 0.0f;
    max_signal_ = 0.0f;
    min_signal_ = 4095.0f;
    rms_index_ = 0;
    std::fill(rms_buffer_.begin(), rms_buffer_.end(), 0.0f);
}

