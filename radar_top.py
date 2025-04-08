from gnu_radio_radar import RADAR
import signal
import sys
import numpy as np
import time
import threading
from config import CONFIG


class RADAR_TOP:
    begin_save_buffer = False
    currently_saving_buffer = False

    tb = None

    def __init__(self):
        self.begin_save_buffer = False

    def start_radar(self):
        """Function to start the radar and handle signals"""
        def sig_handler(sig=None, frame=None):
            self.tb.stop()
            self.tb.wait()
            sys.exit(0)

        # signal.signal(signal.SIGINT, sig_handler)
        # signal.signal(signal.SIGTERM, sig_handler)

        self.tb.start()
        return True

    def save_buffer(self):

        # Don't start saving to file until flag is set
        while (not self.begin_save_buffer):
            pass

        self.currently_saving_buffer = True
        time.sleep(CONFIG.symetric_record_time)  # Wait for 1 second before saving
        print(f"creating buffer from the queue block...")
        buffer = self.tb.queue_block.buffer
        filename = CONFIG.file_name

        print(f"creating copy of buffer")
        buffer_copy = np.array(list(buffer))  # Create a copy for writing
        try:
            with open(filename, "wb") as f:  # Open in write binary mode ("wb") to overwrite
                buffer_copy.tofile(f)
            print(f"Buffer written to {filename}")
        except Exception as e:
            print(f"Error writing to file: {e}")

        # self.disarm()
        print("stop buffer save")
        self.currently_saving_buffer = False
        return True

    def disarm(self):
        print("Disarming radar...")
        self.tb.stop()
        self.tb.wait()
        return True

    def arm(self):
        # GPIO setup (if applicable)
        # GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Start the radar and buffer saving process
        top_block_cls = RADAR
        self.tb = top_block_cls()
        print("Arming radar...")

        # Start the radar in a separate thread
        radar_thread = threading.Thread(target=self.start_radar, args=())
        radar_thread.daemon = True  # Ensures the thread exits when the main program exits
        radar_thread.start()
        
        # Start saving the buffer in a separate thread after 1 second
        save_thread = threading.Thread(target=self.save_buffer, args=())
        save_thread.start()

        save_thread.join()  # Wait for save thread to finish before exiting
        print("Exiting program...")
        return True

