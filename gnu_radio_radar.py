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
from gnuradio import soapy
import fifo_queue_block as queue  # embedded python block
from config import CONFIG




class RADAR(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "MULT_CONJ", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = CONFIG.samp_rate
        self.decimation1 = decimation1 = 1
        self.freq_cutoff = freq_cutoff = (samp_rate/decimation1)/4.5
        self.rf_freq = rf_freq = CONFIG.rf_freq
        self.record_time = record_time = CONFIG.symetric_record_time
        self.gain = gain = CONFIG.sdr_gain
        self.freq_offset = freq_offset = freq_cutoff/2
        self.freq = freq = CONFIG.transmit_freq

        ##################################################
        # Blocks
        ##################################################
        self.soapy_limesdr_source_0 = None
        dev = 'driver=lime'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_limesdr_source_0 = soapy.source(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)
        self.soapy_limesdr_source_0.set_sample_rate(0, samp_rate)
        self.soapy_limesdr_source_0.set_bandwidth(0, 0.0)
        self.soapy_limesdr_source_0.set_frequency(0, rf_freq)
        self.soapy_limesdr_source_0.set_frequency_correction(0, 0)
        self.soapy_limesdr_source_0.set_gain(0, min(max(gain, -12.0), 61.0))
        self.soapy_limesdr_sink_0 = None
        dev = 'driver=lime'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_limesdr_sink_0 = soapy.sink(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)
        self.soapy_limesdr_sink_0.set_sample_rate(0, samp_rate)
        self.soapy_limesdr_sink_0.set_bandwidth(0, 0.0)
        self.soapy_limesdr_sink_0.set_frequency(0, rf_freq)
        self.soapy_limesdr_sink_0.set_frequency_correction(0, 0)
        self.soapy_limesdr_sink_0.set_gain(0, min(max(gain, -12.0), 64.0))
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            decimation1,
            firdes.low_pass(
                40,
                samp_rate,
                freq_cutoff,
                1000,
                window.WIN_HAMMING,
                6.76))
        self.queue_block = queue.fifo_queue(capacity=(int)(samp_rate*record_time*2))
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, freq, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.soapy_limesdr_sink_0, 0))
        # self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.low_pass_filter_0, 0))
        # self.connect((self.low_pass_filter_0, 0), (self.queue_block, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.queue_block, 0))
        self.connect((self.soapy_limesdr_source_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_freq_cutoff((self.samp_rate/self.decimation1)/2.5)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.queue_block.capacity = self.samp_rate/self.decimation1
        self.low_pass_filter_0.set_taps(firdes.low_pass(40, self.samp_rate, self.freq_cutoff, 1000, window.WIN_HAMMING, 6.76))
        self.soapy_limesdr_sink_0.set_sample_rate(0, self.samp_rate)
        self.soapy_limesdr_source_0.set_sample_rate(0, self.samp_rate)

    def get_decimation1(self):
        return self.decimation1

    def set_decimation1(self, decimation1):
        self.decimation1 = decimation1
        self.set_freq_cutoff((self.samp_rate/self.decimation1)/2.5)
        self.queue_block.capacity = self.samp_rate/self.decimation1

    def get_freq_cutoff(self):
        return self.freq_cutoff

    def set_freq_cutoff(self, freq_cutoff):
        self.freq_cutoff = freq_cutoff
        self.set_freq_offset(self.freq_cutoff/2)
        self.low_pass_filter_0.set_taps(firdes.low_pass(40, self.samp_rate, self.freq_cutoff, 1000, window.WIN_HAMMING, 6.76))

    def get_rf_freq(self):
        return self.rf_freq

    def set_rf_freq(self, rf_freq):
        self.rf_freq = rf_freq
        self.soapy_limesdr_sink_0.set_frequency(0, self.rf_freq)
        self.soapy_limesdr_source_0.set_frequency(0, self.rf_freq)

    def get_record_time(self):
        return self.record_time

    def set_record_time(self, record_time):
        self.record_time = record_time

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.soapy_limesdr_sink_0.set_gain(0, min(max(self.gain, -12.0), 64.0))
        self.soapy_limesdr_source_0.set_gain(0, min(max(self.gain, -12.0), 61.0))

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.analog_sig_source_x_0.set_frequency(self.freq)