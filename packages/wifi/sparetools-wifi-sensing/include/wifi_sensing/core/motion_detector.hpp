#pragma once

#include <vector>
#include <Eigen/Dense>

namespace wifi_sensing {
namespace core {

class MotionDetector {
public:
    MotionDetector();
    ~MotionDetector() = default;

    /**
     * Analyze CSI fluctuations to detect motion
     * @param csi_data CSI amplitude data (complex numbers)
     * @return true if motion detected
     */
    bool analyze_fluctuations(const Eigen::MatrixXcd& csi_data);

    /**
     * Set motion detection threshold
     * @param threshold Sensitivity threshold (0.0-1.0)
     */
    void set_threshold(double threshold);

    /**
     * Get current motion detection threshold
     * @return Current threshold value
     */
    double get_threshold() const;

private:
    double threshold_;
    std::vector<double> history_;
};

} // namespace core
} // namespace wifi_sensing