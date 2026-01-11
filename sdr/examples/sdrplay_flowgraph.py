#!/usr/bin/env python3
"""
Basic SDRplay RSP1 GNU Radio Flowgraph
Generated automatically - demonstrates SDRplay usage
"""

from gnuradio import gr, blocks, audio
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation

class sdrplay_test(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "SDRplay Test Flowgraph")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2000000  # 2 MSPS
        self.center_freq = center_freq = 100000000  # 100 MHz

        ##################################################
        # Blocks
        ##################################################

        # Try SDRplay source first
        try:
            from gnuradio import soapy
            self.soapy_sdrplay_source_0 = soapy.source(1, "driver=sdrplay",
                1, "", [''], [''], samp_rate, "fc32")
            self.soapy_sdrplay_source_0.set_sample_rate(0, samp_rate)
            self.soapy_sdrplay_source_0.set_frequency(0, center_freq)
            self.soapy_sdrplay_source_0.set_gain(0, 20)  # 20 dB gain
            print("Using SoapySDR SDRplay source")
        except:
            # Fallback to generic SDR source
            try:
                self.osmosdr_source_0 = osmosdr.source(args="numchan=" + str(1) + " " + "")
                self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
                self.osmosdr_source_0.set_sample_rate(samp_rate)
                self.osmosdr_source_0.set_center_freq(center_freq, 0)
                self.osmosdr_source_0.set_freq_corr(0, 0)
                self.osmosdr_source_0.set_dc_offset_mode(0, 0)
                self.osmosdr_source_0.set_iq_balance_mode(0, 0)
                self.osmosdr_source_0.set_gain_mode(False, 0)
                self.osmosdr_source_0.set_gain(20, 0)  # 20 dB gain
                self.osmosdr_source_0.set_if_gain(20, 0)
                self.osmosdr_source_0.set_bb_gain(20, 0)
                self.osmosdr_source_0.set_antenna("", 0)
                self.osmosdr_source_0.set_bandwidth(0, 0)
                print("Using Osmocom SDR source (may not work with SDRplay)")
            except:
                print("No suitable SDR source found!")
                print("Install SDRplay GNU Radio blocks or use SoapySDR")
                sys.exit(1)

        # Audio sink for testing
        self.audio_sink_0 = audio.sink(48000, "", True)

        # Resampler to audio rate
        self.rational_resampler_xxx_0 = blocks.rational_resampler_ccc(
                interpolation=48,
                decimation=100,
                taps=[],
                fractional_bw=0)

        # AM demodulator for testing
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)

        # Audio resampler
        self.blocks_float_to_short_0 = blocks.float_to_short(1, 32767)

        ##################################################
        # Connections
        ##################################################
        try:
            self.connect((self.soapy_sdrplay_source_0, 0), (self.rational_resampler_xxx_0, 0))
        except:
            self.connect((self.osmosdr_source_0, 0), (self.rational_resampler_xxx_0, 0))

        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_float_to_short_0, 0))
        self.connect((self.blocks_float_to_short_0, 0), (self.audio_sink_0, 0))

def main(top_block_cls=sdrplay_test, options=None):
    tb = top_block_cls()
    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    print("GNU Radio flowgraph started...")
    print("Tuned to 100 MHz with 20 dB gain")
    print("Listening for AM signals...")
    print("Press Ctrl+C to stop")

    try:
        input("Press Enter to quit or Ctrl+C...")
    except EOFError:
        pass
    tb.stop()
    tb.wait()

if __name__ == '__main__':
    main()
