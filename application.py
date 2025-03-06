from gnu_radio_radar import RADAR
import signal
import sys
import numpy as np
import time
import threading
from config import CONFIG

def start_radar(tb):
    """Function to start the radar and handle signals"""
    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    # signal.signal(signal.SIGINT, sig_handler)
    # signal.signal(signal.SIGTERM, sig_handler)
    tb.start()

def save_buffer(tb):
    """Function to save the buffer after 1 second"""

    # Wait for a short time before saving the buffer
    input('Press Enter to exit and save: ')

    time.sleep(CONFIG.symetric_record_time)  # Wait for 1 second before saving
    buffer = tb.queue_block.buffer
    filename = CONFIG.file_name


    buffer_copy = np.array(list(buffer))  # Create a copy for writing
    try:
        with open(filename, "wb") as f:  # Open in write binary mode ("wb") to overwrite
            buffer_copy.tofile(f)
        print(f"Buffer written to {filename}")
    except Exception as e:
        print(f"Error writing to file: {e}")

    tb.stop()
    tb.wait()

def main():
    # GPIO setup (if applicable)
    # GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Start the radar and buffer saving process
    input('Press enter to start: ')
    top_block_cls = RADAR
    tb = top_block_cls()

    # Start the radar in a separate thread
    radar_thread = threading.Thread(target=start_radar, args=(tb,))
    radar_thread.daemon = True  # Ensures the thread exits when the main program exits
    radar_thread.start()
    
    # Start saving the buffer in a separate thread after 1 second
    save_thread = threading.Thread(target=save_buffer, args=(tb,))
    save_thread.start()

    save_thread.join()  # Wait for save thread to finish before exiting
    print("Exiting program...")

if __name__ == '__main__':
    main()
