import numpy as np
from gnuradio import gr
from collections import deque

class fifo_queue(gr.sync_block):
    def __init__(self, capacity=4000000):
        gr.sync_block.__init__(self,
            name="FIFO Queue",
            in_sig=[np.complex64],
            out_sig=None)

        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.data_type = np.complex64
        print("Buffer initialized")


    def work(self, input_items, output_items):
        in_data = input_items[0]
        #print(len(in_data))

        self.buffer.extend(in_data)

        return len(input_items[0])