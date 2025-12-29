#!/usr/bin/env python3
"""
Mock ESP32 BPM Detector API Server for Testing
Simulates the HTTP REST API that would run on ESP32
"""

import json
import time
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Mock BPM state
bpm_state = {
    "bpm": 128.5,
    "confidence": 0.87,
    "signal_level": 0.72,
    "status": "detecting",
    "timestamp": int(time.time() * 1000)
}

@app.route('/api/bpm', methods=['GET'])
def get_bpm():
    """Mock /api/bpm endpoint"""
    bpm_state["timestamp"] = int(time.time() * 1000)
    return jsonify(bpm_state)

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Mock /api/settings endpoint"""
    return jsonify({
        "min_bpm": 60,
        "max_bpm": 200,
        "sample_rate": 25000,
        "fft_size": 1024,
        "version": "1.0.0"
    })

@app.route('/api/health', methods=['GET'])
def get_health():
    """Mock /api/health endpoint"""
    return jsonify({
        "status": "ok",
        "uptime": int(time.time()),
        "heap_free": 245760
    })

if __name__ == '__main__':
    print("Starting Mock ESP32 BPM Detector API Server...")
    print("Endpoints:")
    print("  GET /api/bpm - Current BPM data")
    print("  GET /api/settings - Configuration")
    print("  GET /api/health - Health status")
    app.run(host='127.0.0.1', port=9090, debug=False)
