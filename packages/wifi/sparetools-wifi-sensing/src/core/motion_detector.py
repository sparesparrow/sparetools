#!/usr/bin/env python3
"""
WiFi Motion Detection Module
Implements motion detection algorithms using WiFi signal fluctuations
"""

import numpy as np
from collections import deque
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MotionDetector:
    """
    Motion detector using WiFi signal analysis.

    This class implements various algorithms for detecting motion through walls
    using WiFi signal strength fluctuations and statistical analysis.
    """

    def __init__(self, history_size=100, variance_threshold=50, min_samples=5):
        """
        Initialize motion detector.

        Args:
            history_size (int): Number of signal samples to keep in history
            variance_threshold (float): Threshold for detecting motion via variance
            min_samples (int): Minimum samples needed for analysis
        """
        self.history_size = history_size
        self.variance_threshold = variance_threshold
        self.min_samples = min_samples

        # Signal history: {mac_address: deque of (timestamp, signal_strength)}
        self.signal_history = {}

        # Motion events log
        self.motion_events = deque(maxlen=100)

    def update_signal(self, mac_address, signal_strength, timestamp=None):
        """
        Update signal strength for a WiFi network.

        Args:
            mac_address (str): MAC address of the access point
            signal_strength (float): Signal strength in dBm
            timestamp (datetime): Timestamp of measurement (default: now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        if mac_address not in self.signal_history:
            self.signal_history[mac_address] = deque(maxlen=self.history_size)

        self.signal_history[mac_address].append((timestamp, signal_strength))

    def analyze_signal_fluctuations(self, mac_address=None):
        """
        Analyze signal fluctuations for motion detection.

        Args:
            mac_address (str): Specific MAC to analyze, or None for all

        Returns:
            dict: Analysis results with motion detection status
        """
        results = {}

        macs_to_analyze = [mac_address] if mac_address else list(self.signal_history.keys())

        for mac in macs_to_analyze:
            if mac not in self.signal_history:
                continue

            history = list(self.signal_history[mac])
            if len(history) < self.min_samples:
                continue

            # Extract signal values
            signals = [entry[1] for entry in history]
            timestamps = [entry[0] for entry in history]

            # Calculate statistical measures
            variance = np.var(signals)
            std_dev = np.std(signals)
            mean_signal = np.mean(signals)
            signal_range = np.ptp(signals)  # peak-to-peak

            # Motion detection based on variance
            motion_detected = variance > self.variance_threshold

            # Calculate signal stability (lower is more stable)
            stability_score = variance / (abs(mean_signal) + 1)  # Normalize by signal strength

            results[mac] = {
                'motion_detected': motion_detected,
                'variance': variance,
                'std_dev': std_dev,
                'mean_signal': mean_signal,
                'signal_range': signal_range,
                'stability_score': stability_score,
                'sample_count': len(signals),
                'last_timestamp': timestamps[-1]
            }

            # Log motion events
            if motion_detected:
                motion_event = {
                    'timestamp': datetime.now(),
                    'mac_address': mac,
                    'variance': variance,
                    'signal_stats': results[mac]
                }
                self.motion_events.append(motion_event)
                logger.info(f"Motion detected for {mac}: variance={variance:.2f}")

        return results

    def detect_motion_patterns(self, time_window_seconds=30):
        """
        Detect motion patterns over a time window.

        Args:
            time_window_seconds (int): Time window for pattern analysis

        Returns:
            dict: Pattern analysis results
        """
        now = datetime.now()
        window_start = now.timestamp() - time_window_seconds

        # Collect events in time window
        recent_events = [
            event for event in self.motion_events
            if event['timestamp'].timestamp() > window_start
        ]

        if not recent_events:
            return {'pattern': 'no_motion', 'event_count': 0}

        # Analyze patterns
        event_count = len(recent_events)
        avg_variance = np.mean([e['variance'] for e in recent_events])

        # Classify motion patterns
        if event_count < 2:
            pattern = 'occasional_motion'
        elif event_count < 5:
            pattern = 'moderate_activity'
        else:
            pattern = 'high_activity'

        return {
            'pattern': pattern,
            'event_count': event_count,
            'avg_variance': avg_variance,
            'time_window': time_window_seconds,
            'events': recent_events
        }

    def get_motion_statistics(self):
        """
        Get overall motion detection statistics.

        Returns:
            dict: Statistics about motion detection performance
        """
        total_events = len(self.motion_events)

        if total_events == 0:
            return {'total_events': 0, 'message': 'No motion events recorded'}

        # Calculate statistics
        variances = [e['variance'] for e in self.motion_events]
        timestamps = [e['timestamp'] for e in self.motion_events]

        time_span = (max(timestamps) - min(timestamps)).total_seconds() if len(timestamps) > 1 else 0

        return {
            'total_events': total_events,
            'avg_variance': np.mean(variances),
            'max_variance': np.max(variances),
            'time_span_seconds': time_span,
            'events_per_minute': (total_events / max(time_span / 60, 1)) if time_span > 0 else 0,
            'networks_monitored': len(self.signal_history)
        }

    def reset(self):
        """Reset motion detector state."""
        self.signal_history.clear()
        self.motion_events.clear()
        logger.info("Motion detector reset")

    def __repr__(self):
        return f"MotionDetector(networks={len(self.signal_history)}, events={len(self.motion_events)})"