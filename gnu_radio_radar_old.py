#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: RADAR
# GNU Radio version: 3.10.1.1

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import fifo_queue_block as queue  # embedded python block
import limesdr

import numpy as np
#import RPi.GPIO as GPIO


class RADAR(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "RADAR", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 4000000
        self.decimation1 = decimation1 = 1
        self.freq_cutoff = freq_cutoff = (samp_rate/decimation1)/2.5
        self.rf_freq = rf_freq = 1000000000
        self.record_time = record_time = 1
        self.gain = gain = 25
        self.freq_offset = freq_offset = freq_cutoff/2
        self.freq = freq = 1000000

        ##################################################
        # Blocks
        ##################################################
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            decimation1,
            firdes.low_pass(
                20,
                samp_rate,
                freq_cutoff,
                1000,
                window.WIN_HAMMING,
                6.76))
        self.limesdr_source_0 = limesdr.source('', 0, '')
        self.limesdr_source_0.set_sample_rate(samp_rate)
        self.limesdr_source_0.set_center_freq(rf_freq, 0)
        self.limesdr_source_0.set_bandwidth(5e6, 0)
        self.limesdr_source_0.set_gain(gain,0)
        self.limesdr_source_0.set_antenna(255,0)
        self.limesdr_source_0.calibrate(5e6, 0)
        self.limesdr_sink_0 = limesdr.sink('', 0, '', '')
        self.limesdr_sink_0.set_sample_rate(samp_rate)
        self.limesdr_sink_0.set_center_freq(rf_freq, 0)
        self.limesdr_sink_0.set_bandwidth(5e6,0)
        self.limesdr_sink_0.set_gain(gain,0)
        self.limesdr_sink_0.set_antenna(255,0)
        self.limesdr_sink_0.calibrate(5e6, 0)
        self.high_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.high_pass(
                1,
                samp_rate,
                10000,
                1000,
                window.WIN_HAMMING,
                6.76))
        self.queue_block = queue.fifo_queue(capacity=samp_rate)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_head_0 = blocks.head(gr.sizeof_gr_complex*1, 4000000)
        #self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, '/home/collin_lambert/SDR_PYTHON/feb19.bin', False)
        #self.blocks_file_sink_0.set_unbuffered(False)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, freq, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.limesdr_sink_0, 0))
        #self.connect((self.blocks_head_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.high_pass_filter_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.limesdr_source_0, 0), (self.high_pass_filter_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_head_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.queue_block, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_freq_cutoff((self.samp_rate/self.decimation1)/2.5)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.queue_block.capacity = self.samp_rate
        self.high_pass_filter_0.set_taps(firdes.high_pass(1, self.samp_rate, 10000, 1000, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_0.set_taps(firdes.low_pass(20, self.samp_rate, self.freq_cutoff, 1000, window.WIN_HAMMING, 6.76))

    def get_decimation1(self):
        return self.decimation1

    def set_decimation1(self, decimation1):
        self.decimation1 = decimation1
        self.set_freq_cutoff((self.samp_rate/self.decimation1)/2.5)

    def get_freq_cutoff(self):
        return self.freq_cutoff

    def set_freq_cutoff(self, freq_cutoff):
        self.freq_cutoff = freq_cutoff
        self.set_freq_offset(self.freq_cutoff/2)
        self.low_pass_filter_0.set_taps(firdes.low_pass(20, self.samp_rate, self.freq_cutoff, 1000, window.WIN_HAMMING, 6.76))

    def get_rf_freq(self):
        return self.rf_freq

    def set_rf_freq(self, rf_freq):
        self.rf_freq = rf_freq
        self.limesdr_sink_0.set_center_freq(self.rf_freq, 0)
        self.limesdr_source_0.set_center_freq(self.rf_freq, 0)

    def get_record_time(self):
        return self.record_time

    def set_record_time(self, record_time):
        self.record_time = record_time

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.limesdr_sink_0.set_gain(self.gain,0)
        self.limesdr_source_0.set_gain(self.gain,0)

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.analog_sig_source_x_0.set_frequency(self.freq)

