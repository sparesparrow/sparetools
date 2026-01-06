#!/bin/bash
# SDR Setup Guide and Quick Commands

echo "=== SDR Setup Guide ==="
echo
echo "Your SDR environment is now set up with:"
echo "• SDRplay RSP1 device detected via USB"
echo "• SDRplay API installed"
echo "• GNU Radio framework"
echo "• SoapySDR abstraction library"
echo "• Additional SDR software (gqrx, inspectrum, etc.)"
echo

echo "=== Quick Commands ==="
echo
echo "1. Check SDR devices:"
echo "   python3 sdr_device_info.py"
echo "   python3 sdr_sdrplay_test.py    # SDRplay-specific test"
echo
echo "2. Create GNU Radio example:"
echo "   python3 sdrplay_gnuradio_example.py"
echo "   python3 sdrplay_flowgraph.py        # Run the example"
echo
echo "3. RTL-SDR tools (if you also have RTL-SDR):"
echo "   python3 sdr_scanner.py -f 100.0"
echo "   python3 sdr_fm_radio.py -f 88.5"
echo
echo "4. Launch SDR GUIs:"
echo "   gqrx                    # Popular SDR GUI"
echo "   cubicsdr               # CubicSDR"
echo "   inspectrum             # Signal analysis"
echo
echo "5. GNU Radio:"
echo "   gnuradio-companion     # Flowgraph editor"
echo
echo "6. RTL-SDR commands:"
echo "   rtl_test               # Test RTL-SDR"
echo "   rtl_fm -f 88.5M -M fm -s 170k -A fast -r 32k -l 0 -g 20 | play -r 32k -t raw -e s -b 16 -c 1 -V1 -"
echo
echo "7. SoapySDR:"
echo "   SoapySDRUtil --find    # List devices"
echo "   SoapySDRUtil --probe   # Device info"
echo

echo "=== SDRplay RSP1 Notes ==="
echo "• Frequency range: 1 kHz to 2 GHz"
echo "• Maximum bandwidth: 10 MHz"
echo "• Sample rates up to 10 MSPS"
echo "• Uses proprietary SDRplay API (not RTL-SDR compatible)"
echo "• Best Linux support via GNU Radio + SoapySDR"
echo "• For full features, SDRuno software (Windows) is recommended"
echo "• GQRX has limited SDRplay support"
echo

echo "=== Troubleshooting ==="
echo "• If devices aren't detected: check USB connection"
echo "• For permission issues: add user to plugdev group"
echo "• RTL-SDR kernel issues: blacklist rtl2832u module"
echo "• Audio issues: install sox or pulseaudio-utils"
echo

echo "Setup complete! Enjoy exploring the radio spectrum! 📻"