#include "bpm_detector.h"
#include "config.h"
#include "audio_input.h"
#include <arduinoFFT.h>
using namespace std;
#include <cmath>
#include <algorithm>
#include <cstdlib>

BPMDetector::BPMDetector(uint16_t sample_rate, uint16_t fft_size)
    : sample_rate_(sample_rate)
    , fft_size_(fft_size)
    , adc_pin_(0)
    , min_bpm_(MIN_BPM)
    , max_bpm_(MAX_BPM)
    , detection_threshold_(DETECTION_THRESHOLD)
    , envelope_value_(0.0f)
    , envelope_threshold_(0.0f)
    , test_mode_(false)
    , test_frequency_(0.0f)
    , test_phase_(0.0f)
    , audio_input_(nullptr)
    , owns_audio_input_(false)
{
    // Pre-allocate buffers
    sample_buffer_.reserve(fft_size_);
    sample_buffer_.resize(fft_size_, 0.0f);
    
    // FFT buffer only needs half size for magnitude data
    fft_buffer_.reserve(fft_size_ / 2);
    fft_buffer_.resize(fft_size_ / 2, 0.0f);
    
    beat_times_.reserve(BEAT_HISTORY_SIZE);
    
    // Initialize envelope threshold
    envelope_threshold_ = detection_threshold_;
}

BPMDetector::BPMDetector(AudioInput* audio_input, uint16_t sample_rate, uint16_t fft_size)
    : sample_rate_(sample_rate)
    , fft_size_(fft_size)
    , adc_pin_(0)
    , min_bpm_(MIN_BPM)
    , max_bpm_(MAX_BPM)
    , detection_threshold_(DETECTION_THRESHOLD)
    , envelope_value_(0.0f)
    , envelope_threshold_(0.0f)
    , test_mode_(false)
    , test_frequency_(0.0f)
    , test_phase_(0.0f)
    , audio_input_(audio_input)
    , owns_audio_input_(false)
{
    // Pre-allocate buffers
    sample_buffer_.reserve(fft_size_);
    sample_buffer_.resize(fft_size_, 0.0f);
    
    // FFT buffer only needs half size for magnitude data
    fft_buffer_.reserve(fft_size_ / 2);
    fft_buffer_.resize(fft_size_ / 2, 0.0f);
    
    beat_times_.reserve(BEAT_HISTORY_SIZE);
    
    // Initialize envelope threshold
    envelope_threshold_ = detection_threshold_;
}

BPMDetector::~BPMDetector() {
    // Only delete if we own the audio input
    if (owns_audio_input_ && audio_input_) {
        delete audio_input_;
        audio_input_ = nullptr;
    }
}

void BPMDetector::begin(uint8_t adc_pin) {
    adc_pin_ = adc_pin;
    
    // Create audio input instance if not provided
    if (!audio_input_) {
        audio_input_ = new AudioInput();
        audio_input_->begin(adc_pin);
        owns_audio_input_ = true;
    } else {
        // If audio input was injected, initialize it with the pin
        audio_input_->begin(adc_pin);
    }
    
    // Clear buffers
    std::fill(sample_buffer_.begin(), sample_buffer_.end(), 0.0f);
    std::fill(fft_buffer_.begin(), fft_buffer_.end(), 0.0f);
    beat_times_.clear();
    
    envelope_value_ = 0.0f;
    envelope_threshold_ = detection_threshold_;
    
    #if DEBUG_SERIAL
        DEBUG_PRINTF("[BPMDetector] Initialized: sample_rate=%d, fft_size=%d\n", 
                     sample_rate_, fft_size_);
    #endif
}

void BPMDetector::begin(AudioInput* audio_input, uint8_t adc_pin) {
    // Clean up existing audio input if we own it
    if (owns_audio_input_ && audio_input_) {
        delete audio_input_;
    }
    
    audio_input_ = audio_input;
    owns_audio_input_ = false;
    adc_pin_ = adc_pin;
    
    if (audio_input_) {
        audio_input_->begin(adc_pin);
    }
    
    // Clear buffers
    std::fill(sample_buffer_.begin(), sample_buffer_.end(), 0.0f);
    std::fill(fft_buffer_.begin(), fft_buffer_.end(), 0.0f);
    beat_times_.clear();
    
    envelope_value_ = 0.0f;
    envelope_threshold_ = detection_threshold_;
    
    #if DEBUG_SERIAL
        DEBUG_PRINTF("[BPMDetector] Initialized with injected AudioInput: sample_rate=%d, fft_size=%d\n", 
                     sample_rate_, fft_size_);
    #endif
}

void BPMDetector::sample() {
    if (test_mode_) {
        // Generate test signal
        float sample = generateTestSample();
        addSample(sample);
    } else if (audio_input_ && audio_input_->isInitialized()) {
        // Read from actual ADC
        float sample = audio_input_->readSample();
        addSample(sample);
    }
}

void BPMDetector::addSample(float value) {
    // Add sample to circular buffer
    if (sample_buffer_.size() < fft_size_) {
        sample_buffer_.push_back(value);
    } else {
        // Circular buffer: shift left and add new value at end
        for (size_t i = 0; i < fft_size_ - 1; ++i) {
            sample_buffer_[i] = sample_buffer_[i + 1];
        }
        sample_buffer_[fft_size_ - 1] = value;
    }
}

bool BPMDetector::isBufferReady() const {
    return sample_buffer_.size() >= fft_size_;
}

BPMDetector::BPMData BPMDetector::detect() {
    BPMData result;
    result.bpm = 0.0f;
    result.confidence = 0.0f;
    result.signal_level = 0.0f;
    result.status = "initializing";
    result.timestamp = millis();
    
    // Validate initialization
    if (sample_rate_ == 0 || fft_size_ == 0) {
        result.status = "error";
        #if DEBUG_SERIAL
            DEBUG_PRINTLN("[BPMDetector] Error: Invalid configuration");
        #endif
        return result;
    }

    // #region agent log
    extern void writeLog(const char*, const char*, const char*, const char*);
    char dataBuf1[128];
    snprintf(dataBuf1, sizeof(dataBuf1), "{\"bufferReady\":%d,\"bufferSize\":%zu,\"timestamp\":%lu}",
             isBufferReady() ? 1 : 0, sample_buffer_.size(), result.timestamp);
    writeLog("bpm_detector.cpp:detect:entry", "BPM detection started", "C", dataBuf1);
    // #endregion

    // Check if buffer is ready
    if (!isBufferReady()) {
        result.status = "buffering";
        // #region agent log
        writeLog("bpm_detector.cpp:detect:bufferNotReady", "Buffer not ready for detection", "C", "{\"status\":\"buffering\"}");
        // #endregion
        return result;
    }
    
    // Get signal level
    if (audio_input_) {
        result.signal_level = audio_input_->getNormalizedLevel();
    } else {
        // Calculate from sample buffer
        float sum_sq = 0.0f;
        for (float s : sample_buffer_) {
            sum_sq += s * s;
        }
        result.signal_level = sqrt(sum_sq / sample_buffer_.size());
        // Normalize
        if (result.signal_level > 1.0f) result.signal_level = 1.0f;
    }
    
    // Check signal level
    if (result.signal_level < 0.01f) {
        result.status = "low_signal";
        return result;
    }
    
    // Perform FFT
    performFFT();
    
    // Detect beats using envelope detection
    detectBeatEnvelope();
    
    // Calculate BPM
    result.bpm = calculateBPM();
    result.confidence = calculateConfidence();

    // #region agent log
    char dataBuf2[128];
    snprintf(dataBuf2, sizeof(dataBuf2), "{\"calculatedBPM\":%.1f,\"calculatedConfidence\":%.3f,\"signalLevel\":%.3f}",
             result.bpm, result.confidence, result.signal_level);
    writeLog("bpm_detector.cpp:detect:calculation", "BPM calculation completed", "C", dataBuf2);
    // #endregion

    // Determine status
    if (result.bpm > 0.0f && result.confidence >= CONFIDENCE_THRESHOLD) {
        result.status = "detecting";
    } else if (result.bpm > 0.0f) {
        result.status = "low_confidence";
    } else {
        result.status = "no_beats";
    }

    // #region agent log
    char dataBuf3[128];
    snprintf(dataBuf3, sizeof(dataBuf3), "{\"finalBPM\":%.1f,\"finalConfidence\":%.3f,\"status\":\"%s\"}",
             result.bpm, result.confidence, result.status.c_str());
    writeLog("bpm_detector.cpp:detect:complete", "BPM detection completed", "C", dataBuf3);
    // #endregion

    return result;
}

void BPMDetector::performFFT() {
    // ArduinoFFT requires double arrays, so we need to convert
    // Create temporary arrays for real and imaginary parts
    static double* vReal = nullptr;
    static double* vImag = nullptr;
    static bool arrays_allocated = false;
    
    if (!arrays_allocated) {
        vReal = (double*)malloc(fft_size_ * sizeof(double));
        vImag = (double*)malloc(fft_size_ * sizeof(double));
        arrays_allocated = true;
    }
    
    // Copy samples to real array (imaginary part is zero for real signals)
    for (size_t i = 0; i < fft_size_; ++i) {
        vReal[i] = (double)sample_buffer_[i];
        vImag[i] = 0.0;
    }
    
    // Create FFT instance
    ArduinoFFT<double> FFT(vReal, vImag, fft_size_, sample_rate_);

    // Apply window function and perform FFT
    FFT.windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD);
    FFT.compute(FFT_FORWARD);
    FFT.complexToMagnitude();
    
    // Copy magnitude results back to fft_buffer_ for use in beat detection
    for (size_t i = 0; i < fft_size_ / 2; ++i) {
        fft_buffer_[i] = (float)vReal[i];
    }
    
    #if DEBUG_FFT
        // Print FFT bins for debugging
        DEBUG_PRINTLN("[FFT] Frequency bins:");
        for (size_t i = 0; i < fft_size_ / 2; ++i) {
            float freq = (i * sample_rate_) / fft_size_;
            if (freq >= BASS_FREQ_MIN && freq <= BASS_FREQ_MAX) {
                DEBUG_PRINTF("  %.1f Hz: %.2f\n", freq, fft_buffer_[i]);
            }
        }
    #endif
}

void BPMDetector::detectBeatEnvelope() {
    // Calculate bass energy from FFT
    float bass_energy = 0.0f;
    
    // Frequency resolution: sample_rate / fft_size
    float freq_resolution = (float)sample_rate_ / fft_size_;
    
    // Find FFT bins corresponding to bass frequencies (40-200 Hz)
    size_t min_bin = (size_t)(BASS_FREQ_MIN / freq_resolution);
    size_t max_bin = (size_t)(BASS_FREQ_MAX / freq_resolution);
    
    // Clamp to valid range
    if (min_bin >= fft_size_ / 2) min_bin = 0;
    if (max_bin >= fft_size_ / 2) max_bin = fft_size_ / 2 - 1;
    
    // Sum energy in bass frequency range
    for (size_t i = min_bin; i <= max_bin; ++i) {
        bass_energy += fft_buffer_[i];
    }
    
    // Normalize by number of bins
    bass_energy /= (max_bin - min_bin + 1);
    
    // Update envelope with decay/release
    if (bass_energy > envelope_value_) {
        // Attack: fast rise
        envelope_value_ = bass_energy;
    } else {
        // Decay/Release: exponential decay
        envelope_value_ = envelope_value_ * ENVELOPE_DECAY + bass_energy * (1.0f - ENVELOPE_DECAY);
    }
    
    // Adaptive threshold based on signal level
    float signal_level = 0.0f;
    if (audio_input_) {
        signal_level = audio_input_->getNormalizedLevel();
    }
    
    // Adjust threshold based on signal level
    envelope_threshold_ = detection_threshold_ * (0.5f + signal_level * 0.5f);
    
    // Detect beat when envelope crosses threshold
    static float prev_envelope = 0.0f;
    unsigned long current_time = millis();
    
    // Check for beat (rising edge crossing threshold)
    if (envelope_value_ > envelope_threshold_ && prev_envelope <= envelope_threshold_) {
        // Check minimum beat interval
        if (beat_times_.empty() || 
            (current_time - beat_times_.back()) >= MIN_BEAT_INTERVAL) {
            
            beat_times_.push_back(current_time);
            
            // Keep only recent beats
            if (beat_times_.size() > BEAT_HISTORY_SIZE) {
                beat_times_.erase(beat_times_.begin());
            }
            
            #if DEBUG_BEATS
                DEBUG_PRINTF("[Beat] Detected at %lu ms, envelope=%.3f\n", 
                           current_time, envelope_value_);
            #endif
        }
    }
    
    prev_envelope = envelope_value_;
}

float BPMDetector::calculateBPM() {
    if (beat_times_.size() < 2) {
        return 0.0f;
    }
    
    // Calculate intervals between beats
    std::vector<float> intervals;
    intervals.reserve(beat_times_.size() - 1);
    
    for (size_t i = 1; i < beat_times_.size(); ++i) {
        float interval_ms = beat_times_[i] - beat_times_[i - 1];
        
        // Filter out invalid intervals
        if (interval_ms >= MIN_BEAT_INTERVAL && interval_ms <= MAX_BEAT_INTERVAL) {
            intervals.push_back(interval_ms);
        }
    }
    
    if (intervals.empty()) {
        return 0.0f;
    }
    
    // Calculate average interval (use median for robustness)
    std::sort(intervals.begin(), intervals.end());
    
    float median_interval;
    if (intervals.size() % 2 == 0) {
        // Even number: average of two middle values
        median_interval = (intervals[intervals.size() / 2 - 1] + 
                          intervals[intervals.size() / 2]) / 2.0f;
    } else {
        // Odd number: middle value
        median_interval = intervals[intervals.size() / 2];
    }
    
    // Convert interval (ms) to BPM
    // BPM = 60000 / interval_ms
    float bpm = 60000.0f / median_interval;
    
    // Clamp to valid range
    if (bpm < min_bpm_) bpm = 0.0f;
    if (bpm > max_bpm_) bpm = 0.0f;
    
    return bpm;
}

float BPMDetector::calculateConfidence() {
    if (beat_times_.size() < 3) {
        return 0.0f;
    }
    
    // Calculate intervals
    std::vector<float> intervals;
    intervals.reserve(beat_times_.size() - 1);
    
    for (size_t i = 1; i < beat_times_.size(); ++i) {
        float interval_ms = beat_times_[i] - beat_times_[i - 1];
        if (interval_ms >= MIN_BEAT_INTERVAL && interval_ms <= MAX_BEAT_INTERVAL) {
            intervals.push_back(interval_ms);
        }
    }
    
    if (intervals.empty()) {
        return 0.0f;
    }
    
    // Calculate coefficient of variation (std dev / mean)
    float sum = 0.0f;
    for (float interval : intervals) {
        sum += interval;
    }
    float mean = sum / intervals.size();
    
    if (mean < 1.0f) {
        return 0.0f;
    }
    
    float variance = 0.0f;
    for (float interval : intervals) {
        float diff = interval - mean;
        variance += diff * diff;
    }
    variance /= intervals.size();
    float std_dev = sqrtf(variance);
    
    // Coefficient of variation
    float cv = std_dev / mean;
    
    // Convert to confidence (0.0-1.0)
    // Lower CV = higher confidence
    // CV of 0.0 = perfect regularity = confidence 1.0
    // CV of 0.5 = high variation = confidence ~0.0
    float confidence = 1.0f - (cv * 2.0f);
    if (confidence < 0.0f) confidence = 0.0f;
    if (confidence > 1.0f) confidence = 1.0f;
    
    return confidence;
}

void BPMDetector::setMinBPM(float min_bpm) {
    if (min_bpm > 0.0f && min_bpm < max_bpm_) {
        min_bpm_ = min_bpm;
    } else {
        #if DEBUG_SERIAL
            DEBUG_PRINTF("[BPMDetector] Warning: Invalid min_bpm %.1f (must be > 0 and < max_bpm %.1f)\n", 
                        min_bpm, max_bpm_);
        #endif
    }
}

void BPMDetector::setMaxBPM(float max_bpm) {
    if (max_bpm > min_bpm_ && max_bpm <= 300.0f) {
        max_bpm_ = max_bpm;
    } else {
        #if DEBUG_SERIAL
            DEBUG_PRINTF("[BPMDetector] Warning: Invalid max_bpm %.1f (must be > min_bpm %.1f and <= 300)\n", 
                        max_bpm, min_bpm_);
        #endif
    }
}

void BPMDetector::setThreshold(float threshold) {
    if (threshold >= 0.0f && threshold <= 1.0f) {
        detection_threshold_ = threshold;
        envelope_threshold_ = threshold;
    } else {
        #if DEBUG_SERIAL
            DEBUG_PRINTF("[BPMDetector] Warning: Invalid threshold %.2f (must be 0.0-1.0)\n", threshold);
        #endif
    }
}

float BPMDetector::getMinBPM() const {
    return min_bpm_;
}

float BPMDetector::getMaxBPM() const {
    return max_bpm_;
}

// Test mode methods
void BPMDetector::enableTestMode(float frequency_hz) {
    test_mode_ = true;
    test_frequency_ = frequency_hz;
    test_phase_ = 0.0f;
    
    #if DEBUG_SERIAL
        DEBUG_PRINTF("[BPMDetector] Test mode enabled: %.1f Hz\n", frequency_hz);
    #endif
}

void BPMDetector::disableTestMode() {
    test_mode_ = false;
    test_frequency_ = 0.0f;
    test_phase_ = 0.0f;
    
    #if DEBUG_SERIAL
        DEBUG_PRINTLN("[BPMDetector] Test mode disabled");
    #endif
}

float BPMDetector::generateTestSample() {
    if (!test_mode_ || test_frequency_ <= 0.0f) {
        return 0.0f;
    }
    
    // Generate sine wave at test frequency
    float sample = sinf(test_phase_);
    
    // Update phase
    float phase_increment = 2.0f * M_PI * test_frequency_ / sample_rate_;
    test_phase_ += phase_increment;
    
    // Wrap phase to prevent overflow
    if (test_phase_ > 2.0f * M_PI) {
        test_phase_ -= 2.0f * M_PI;
    }
    
    return sample;
}

