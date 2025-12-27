#pragma once

#include <vector>
#include <complex>
#include <Eigen/Dense>

namespace wifi_sensing {
namespace core {

struct CSIFrame {
    std::vector<std::complex<double>> amplitudes;
    std::vector<double> phases;
    uint64_t timestamp;
    uint32_t frame_count;
};

/**
 * CSI Processor for Channel State Information processing
 */
class CSIProcessor {
public:
    CSIProcessor();
    ~CSIProcessor() = default;

    /**
     * Process raw CSI data from Intel 5300 or Atheros chipsets
     * @param raw_data Raw CSI data buffer
     * @return Processed CSI frame
     */
    CSIFrame process_raw_data(const std::vector<uint8_t>& raw_data);

    /**
     * Extract CSI amplitudes and phases
     * @param csi_matrix CSI matrix (subcarriers x antennas)
     * @return Processed CSI frame
     */
    CSIFrame extract_csi(const Eigen::MatrixXcd& csi_matrix);

    /**
     * Apply phase sanitization
     * @param csi_frame Input CSI frame
     * @return Sanitized CSI frame
     */
    CSIFrame sanitize_phases(const CSIFrame& csi_frame);

    /**
     * Set processing parameters
     * @param num_subcarriers Number of subcarriers
     * @param num_antennas Number of antennas
     */
    void set_parameters(size_t num_subcarriers, size_t num_antennas);

private:
    size_t num_subcarriers_;
    size_t num_antennas_;
};

} // namespace core
} // namespace wifi_sensing