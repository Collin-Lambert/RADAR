import tkinter as tk
from tkinter import StringVar, OptionMenu, ttk, messagebox
import os
# import the application file from Radar Files folder
from radar_top import RADAR_TOP
import gnu_radio_radar as gr
from config import CONFIG
import threading
import process_data as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial.tools.list_ports
from datetime import datetime
import subprocess

RADAR = RADAR_TOP()

max_velocity = 0
external_trigger = False
device = None

stop_event = threading.Event()  # Used to stop the serial listener thread

def serial_listener():
    """ Continuously listens to the serial port and calls start_buffer() when 0xFF is received. """
    if device is None:
        print("No device found to listen to.")
        return

    try:
        with serial.Serial(device, 9600, timeout=0.01) as ser:
            print(f"Listening to serial port: {device}")
            while not stop_event.is_set():  # Keep running until stopped
                data = ser.read(1)  # Read one byte
                if data:
                    print(f"Received data: {data}")  # Debugging output
                if data == b'\xFF':
                    print("Received data packet: 0xFF")
                    if (str(disarm_button.cget('state')) == 'normal'):
                        window.after(0, start_buffer)
                        print("Scheduled start_buffer()")
                    else:
                        print("Radar is not armed, ignoring external trigger")
    except serial.SerialException as e:
        print(f"Serial error: {e}")

def start_serial_listener():
    """ Starts the serial listener in a background thread if not already running. """
    global serial_thread
    if "serial_thread" in globals() and serial_thread.is_alive():
        print("Serial listener is already running.")
        return  # Prevent multiple threads from running

    stop_event.clear()  # Reset stop flag
    serial_thread = threading.Thread(target=serial_listener, daemon=True)
    serial_thread.start()
    print("Started serial listener thread.")

def stop_serial_listener():
    """ Stops the serial listener thread. """
    stop_event.set()
    print("Stopping serial listener thread.")

ports = serial.tools.list_ports.comports()
for port in ports:

    if (port.description.__contains__("USB2.0-Ser")):
        # Check if the port is a USB serial device
        print(f"Found: {port.device} - {port.description}")
        external_trigger = True
        device = port.device
        start_serial_listener()
        break
    else:
        print(f"Not Found: {port.device} - {port.description}")
        external_trigger = False


def validate_integer(P):
    if P.isdigit() or P == "":
        return True
    else:
        messagebox.showerror("Invalid Input", "Please enter a valid integer.")
        return False

def arm():
    # run apply_changes to make sure the settings are applied
    

    if apply_changes():
    # run the radar
        threading.Thread(target=RADAR.arm).start()
        messagebox.showinfo("RADAR armed", "Radar armed")
        arm_button.config(state="disabled")
        arm_button.grid_remove()
        manual_trigger_button.config(state="normal")
        disarm_button.config(state="normal")
        disarm_button.grid()
        # messagebox.showinfo("Run", "Measuring...\nMeasuring...\nMeasuring...")
        # messagebox.showinfo("Run", "All Done!")
        return True
    else:
        messagebox.showerror("Error", "Settings have not been applied")
        return False

def disarm():
    RADAR.disarm()
    arm_button.config(state="normal")
    arm_button.grid()
    manual_trigger_button.config(state="disabled")
    disarm_button.config(state="disabled")
    disarm_button.grid_remove()
    messagebox.showinfo("RADAR disarmed", "Radar disarmed")
    return True

def apply_changes():
    settings = {}
    settings["Sample Rate Units"] = option_freq.get()
    try:
        int(sample_rate.get())
    except ValueError:
        messagebox.showerror("Error", "Sample Rate must be an integer")
        messagebox.showinfo("Settings Not Applied", "Settings have not been applied")
        return
    if settings["Sample Rate Units"] == "MHz":
        settings["Sample Rate"] = int(sample_rate.get()) * 1000000

    settings["Intermediate Frequency Units"] = option_int_freq.get()
    try:
        float(int_freq.get())
    except ValueError:
        # messagebox.showerror("Error", "Intermediate Frequency must be an integer")
        messagebox.showinfo("Settings Not Applied", "Settings have not been applied")
        return
    if settings["Intermediate Frequency Units"] == "MHz":
        settings["Intermediate Frequency"] = int(float(int_freq.get()) * 1e6)
    
    try:
        int(gain.get())
    except ValueError:
        messagebox.showerror("Error", "Gain must be an integer")
        messagebox.showinfo("Settings Not Applied", "Settings have not been applied")
        return
    settings["Gain"] = gain.get()
    settings["Gain Units"] = option_gain.get()
    settings["FFT Size"] = option_fft.get()
    settings["FFT Overlap"] = option_fft_overlap.get()
    try:
        int(recording_time.get())
    except ValueError:
        messagebox.showerror("Error", "Recording Time must be an integer")
        messagebox.showinfo("Settings Not Applied", "Settings have not been applied")
        return
    
    try:
        int(decimation.get())
    except ValueError:
        messagebox.showerror("Error", "Decimation must be an integer")
        messagebox.showinfo("Settings Not Applied", "Settings have not been applied")
        return
    
    try:
        int(high_pass_cutoff.get())
    except ValueError:
        messagebox.showerror("Error", "High-Pass Cutoff must be an integer")
        messagebox.showinfo("Settings Not Applied", "Settings have not been applied")
        return
    
    settings["High-Pass Cutoff"] = high_pass_cutoff.get()
    settings["Decimation"] = decimation.get()
    settings["Recording Time"] = recording_time.get()
    settings["Recording Time Units"] = option_time.get()
    sample_rates = settings["Sample Rate"]
    if int(settings["Gain"]) < 0 or int(settings["Gain"]) > 60:
        messagebox.showerror("Error", "Gain must be between 0 and 60")
        messagebox.showinfo("Settings Not Applied", "Settings have not been applied")
        return
    if settings["Sample Rate"] < 1000000 or settings["Sample Rate"] > 10000000:
        messagebox.showerror("Error", "Sample Rate must be between 1MHz and 10MHz")
        messagebox.showinfo("Settings Not Applied", "Settings have not been applied")
        return
    if settings["Intermediate Frequency"] < 1e6:
        messagebox.showerror("Error", "Frequency must be greater than or equal to 1MHz")
        messagebox.showinfo("Settings Not Applied", "Settings have not been applied")
        return
    # radar = gr.RADAR()

    with open("settings.txt", "w") as f:
        # write the new settings to the file
        f.write(f"Sample Rate: {sample_rate.get()}\n")
        f.write(f"Sample Rate Units: {option_freq.get()}\n")
        f.write(f"Intermediate Frequency: {int_freq.get()}\n")
        f.write(f"Intermediate Frequency Units: {option_int_freq.get()}\n")
        f.write(f"Gain: {gain.get()}\n")
        f.write(f"Gain Units: {option_gain.get()}\n")
        f.write(f"FFT Size: {option_fft.get()}\n")
        f.write(f"Recording Time: {recording_time.get()}\n")
        f.write(f"Recording Time Units: {option_time.get()}\n")


    CONFIG.samp_rate = int(float(sample_rate.get()) * 1e6)
    CONFIG.transmit_freq = int(float(int_freq.get()) * 1e6)
    CONFIG.sdr_gain = int(gain.get())
    CONFIG.fft_size = int(option_fft.get())
    CONFIG.fft_overlap = int(option_fft_overlap.get())
    CONFIG.symetric_record_time = int(recording_time.get()) / 2
    CONFIG.high_pass_cutoff = int(high_pass_cutoff.get())
    CONFIG.decimation = int(decimation.get())
    
    

    messagebox.showinfo("Settings Applied", "Settings have been applied")

    print(f"sample_rate: {CONFIG.samp_rate}")
    print(f"transmit_freq: {CONFIG.transmit_freq}")
    print(f"sdr_gain: {CONFIG.sdr_gain}")
    print(f"fft_size: {CONFIG.fft_size}")
    print(f"symetric_record_time: {CONFIG.symetric_record_time}")
    print(f"decimation: {CONFIG.decimation}")
    print(f"high_pass_cutoff: {CONFIG.high_pass_cutoff}")
    print(f"fft_overlap: {CONFIG.fft_overlap}")
    print(f"file_name: {CONFIG.file_name}")
    return True

def start_buffer():
    manual_trigger_button.config(state="disabled")

    if (timestamp_var.get()):
        current_time = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
        CONFIG.file_name = f"{file_name.get()}_{current_time}.bin"
    else:
        CONFIG.file_name = f"{file_name.get()}.bin"


    RADAR.begin_save_buffer = True
    RADAR.currently_saving_buffer = True

    print(f"Starting buffer save to {CONFIG.file_name}")
    while(RADAR.currently_saving_buffer):
        pass
    RADAR.begin_save_buffer = False
    messagebox.showinfo("Manual Trigger", "Buffer Saved")
    
    
    arm_button.config(text="arm", state="normal")
    max_velocity = pd.process_data(spectrogram_var.get())
    update_max_velocity(f"{max_velocity:.1f}")

    disarm()

    return True

#
#
#

window = tk.Tk()
window.title("PotaDAR")

# adjust the window size
window.geometry("1000x800")

pad = 3


tk.Label(window, text="Settings", font=("Arial", 24, "bold")).grid(row=0, column=1, pady=pad)

validate_int_cmd = window.register(validate_integer)


# add a box for the user to input the sample rate and set a default value of 4MHz
tk.Label(window, text="Sample Rate: ").grid(row=1, column=0, pady=pad, sticky='e')
sample_rate = tk.Entry(window)
sample_rate.insert(0, "6")
# sample_rate.bind("<FocusIn>", show_keyboard)  # Open keyboard when clicked
# sample_rate.bind("<FocusOut>", hide_keyboard)
sample_rate.grid(row=1, column=1, pady=pad)
################### BEGIN DROPDOWN ###################
# Create a StringVar to hold the selected value
option_freq = StringVar()
option_freq.set("MHz")  # Set the default value
# Create an OptionMenu
options = ["MHz"]
unit_label = tk.Label(window, textvariable=option_freq, relief="groove", width=5)
unit_label.grid(row=1, column=1, pady=pad, sticky='e')
################### END DROPDOWN #####################
# add on the right side of the box that the default is 4MHz, make it right beside the box
tk.Label(window, text="(Default: 6MHz)", justify="left").grid(row=1, column=2, pady=pad, sticky='w')


# add a field for the user to input the TX frequency
tk.Label(window, text="SDR Frequency: ").grid(row=2, column=0, pady=pad, sticky='e')
int_freq = tk.Entry(window)
int_freq.insert(0, "1.5")
int_freq.grid(row=2, column=1, pady=pad)
################### BEGIN DROPDOWN ###################
# Create a StringVar to hold the selected value
option_int_freq = StringVar()
option_int_freq.set("MHz")  # Set the default value
# Create an OptionMenu
options = ["MHz"]
unit_label = tk.Label(window, textvariable=option_int_freq, relief="groove", width=5)
unit_label.grid(row=2, column=1, pady=pad, sticky='e')
################### END DROPDOWN #####################
tk.Label(window, text="(Default: 1.5MHz)").grid(row=2, column=2, pady=pad, sticky='w')


# add a box for the user to input the gain
tk.Label(window, text="Gain: ").grid(row=3, column=0, pady=pad, sticky='e')
gain = tk.Entry(window)
gain.insert(0, "27")
gain.grid(row=3, column=1, pady=pad)
################### BEGIN DROPDOWN ###################
# Create a Label to show the units
option_gain = StringVar()
option_gain.set("dB")  # Set the default value
# Create a Label to mimic the appearance of an OptionMenu
unit_label = tk.Label(window, textvariable=option_gain, relief="groove", width=5)
unit_label.grid(row=3, column=1, pady=pad, sticky='e')
################### END DROPDOWN #####################
tk.Label(window, text="(Default: 27dB)").grid(row=3, column=2, pady=pad, sticky='w')

# add a box for the user to input the recording time
tk.Label(window, text="Recording Time: ").grid(row=4, column=0, pady=pad, sticky='e')
recording_time = tk.Entry(window)
recording_time.insert(0, "4")
recording_time.grid(row=4, column=1, pady=pad)
################### BEGIN DROPDOWN ###################
# Create a StringVar to hold the selected value
option_time = StringVar()
option_time.set("s")  # Set the default value
# Create an OptionMenu
# options = ["s", "ms"]
unit_label = tk.Label(window, textvariable=option_time, relief="groove", width=5)
unit_label.grid(row=4, column=1, pady=pad, sticky='e')
################### END DROPDOWN #####################
tk.Label(window, text="(Default: 4s)").grid(row=4, column=2, pady=pad, sticky='w')

# add a box for the user to input the high pass cutoff frequency
tk.Label(window, text="High-Pass Cutoff: ").grid(row=5, column=0, pady=pad, sticky='e')
high_pass_cutoff = tk.Entry(window)
high_pass_cutoff.insert(0, "75000")
high_pass_cutoff.grid(row=5, column=1, pady=pad)
################### BEGIN DROPDOWN ###################
# Create a StringVar to hold the selected value
option_high_pass = StringVar()
option_high_pass.set("Hz")  # Set the default value

unit_label = tk.Label(window, textvariable=option_high_pass, relief="groove", width=5)
unit_label.grid(row=5, column=1, pady=pad, sticky='e')
################### END DROPDOWN #####################
tk.Label(window, text="(Default: 75000)").grid(row=5, column=2, pady=pad, sticky='w')

# add a box for the user to input the decimation value
tk.Label(window, text="Decimation: ").grid(row=6, column=0, pady=pad, sticky='e')
decimation = tk.Entry(window)
decimation.insert(0, "2")
decimation.grid(row=6, column=1, pady=pad)
################### BEGIN DROPDOWN ###################
# Create a StringVar to hold the selected value
option_decimation = StringVar()
option_decimation.set("int")  # Set the default value

unit_label = tk.Label(window, textvariable=option_decimation, relief="groove", width=5)
unit_label.grid(row=6, column=1, pady=pad, sticky='e')
################### END DROPDOWN #####################
tk.Label(window, text="(Default: 2)").grid(row=6, column=2, pady=pad, sticky='w')


# add a box for the user to input the FFT size
tk.Label(window, text="FFT Size: ").grid(row=7, column=0, pady=pad, sticky='e')
# fft_size = tk.Entry(window)
# fft_size.insert(0, "1024")
# fft_size.grid(row=4, column=1, pady=10)
tk.Label(window, text="(Default: 1024)").grid(row=7, column=2, pady=pad, sticky='w')
################### BEGIN DROPDOWN ###################
# Create a StringVar to hold the selected value
option_fft = StringVar()
option_fft.set("1024")  # Set the default value
# Create an OptionMenu
options = ["64", "128", "256", "512", "1024", "2048", "4096", "8192"]
dropdown = OptionMenu(window, option_fft, *options)
dropdown.grid(row=7, column=1, pady=pad, sticky='e')
################### END DROPDOWN #####################

# add a box for the user to input the FFT overlap
tk.Label(window, text="FFT Overlap: ").grid(row=8, column=0, pady=pad, sticky='e')
# fft_size = tk.Entry(window)
# fft_size.insert(0, "1024")
# fft_size.grid(row=4, column=1, pady=10)
tk.Label(window, text="(Default: 512)").grid(row=8, column=2, pady=pad, sticky='w')
################### BEGIN DROPDOWN ###################
# Create a StringVar to hold the selected value
option_fft_overlap = StringVar()
option_fft_overlap.set("512")  # Set the default value
# Create an OptionMenu
options = ["64", "128", "256", "512", "1024", "2048", "4096", "8192"]
dropdown = OptionMenu(window, option_fft_overlap, *options)
dropdown.grid(row=8, column=1, pady=pad, sticky='e')
################### END DROPDOWN #####################


# add a box for the user to input the decimation value
tk.Label(window, text="File Name: ").grid(row=3, column=4, pady=pad, sticky='e')
file_name = tk.Entry(window)
file_name.insert(0, "default")
file_name.grid(row=3, column=5, pady=pad)
################### BEGIN DROPDOWN ###################
# Create a StringVar to hold the selected value
option_file_name = StringVar()
option_file_name.set(".bin")  # Set the default value

unit_label = tk.Label(window, textvariable=option_file_name, relief="groove", width=5)
unit_label.grid(row=3, column=5, pady=pad, sticky='e')
################### END DROPDOWN #####################
#tk.Label(window, text="(Default: 2)").grid(row=6, column=2, pady=10, sticky='w')



# add a button that will apply the changes
apply_button = tk.Button(window, text="Apply Changes", command=apply_changes)
apply_button.grid(row=9, column=1, pady=pad)


# Now we will create a column against the right side of the gui that will have output check boxes for spectrogram, velocity, and whether or not to save the data
tk.Label(window, text="Output", font=("Arial", 24, "bold")).grid(row=0, column=5, pady=pad)




# add a check box for the user to select whether or not to display the spectrogram
spectrogram_var = tk.BooleanVar()
spectrogram = tk.Checkbutton(window, text="Show Spectrogram", variable=spectrogram_var)
spectrogram.grid(row=1, column=5, pady=pad)
spectrogram.select()


# add a check box for the user to select whether or not to append the date and time to the file name
timestamp_var = tk.BooleanVar()
timestamp = tk.Checkbutton(window, text="Append Timestamp to File Name", variable=timestamp_var)
timestamp.grid(row=2, column=5, pady=pad)
#timestamp.select()


# # add a check box for the user to select whether or not to save the data
# save_data_var = tk.BooleanVar()
# save_data = tk.Checkbutton(window, text="Save Data", variable=save_data_var)
# save_data.grid(row=3, column=5, pady=10)
# save_data.select()

# add a button that will function as a manual trigger to start the buffer
manual_trigger_button = tk.Button(window, text="Manual Trigger", command=start_buffer, state="disabled")
manual_trigger_button.grid(row=9, column=5, pady=pad)

# arm button
style = ttk.Style()
style.configure("Custom.TButtonArm.TButton", font=("Arial", 14, "bold"))
style.map("Custom.TButtonArm.TButton", background=[("active", "red"), ("!active", "black")], foreground=[("active", "white"), ("!active", "red")])

# insert a run button that will do nothing for now
arm_button = ttk.Button(window, text="arm", command=arm, style="Custom.TButtonArm.TButton")
arm_button.grid(row=9, column=4, pady=pad, padx=20)  # ipadx increases internal horizontal spacing, ipady increases internal vertical spacing
arm_button.config(width=10)  # Set a specific width for the button

# disarm button
style_disarm = ttk.Style()
style_disarm.configure("Custom.TButtonDisarm.TButton", font=("Arial", 14, "bold"))
style_disarm.map("Custom.TButtonDisarm.TButton", background=[("active", "red"), ("!active", "black")], foreground=[("active", "white"), ("!active", "red")])

# insert a run button that will do nothing for now
disarm_button = ttk.Button(window, text="disarm", command=disarm, style="Custom.TButtonDisarm.TButton", state="disabled")
disarm_button.grid(row=9, column=4, pady=pad, padx=20)  # ipadx increases internal horizontal spacing, ipady increases internal vertical spacing
disarm_button.config(width=10)  # Set a specific width for the button
disarm_button.grid_remove()

# add a box to display the maximum velocity
tk.Label(window, text="Max Velocity: ").grid(row=4, column=4, pady=pad, sticky='e')
max_velocity_var = tk.StringVar()
max_velocity_var.set("0")
max_velocity_label = tk.Label(window, textvariable=max_velocity_var, relief="groove", width=20)
max_velocity_label.grid(row=4, column=5, pady=pad, sticky='w')

option_vel = StringVar()
option_vel.set("m/s")  # Set the default value
# Create an OptionMenu
unit_label = tk.Label(window, textvariable=option_vel, relief="groove", width=5)
unit_label.grid(row=4, column=5, pady=pad, sticky='e')

def update_max_velocity(value):
    max_velocity_var.set(value)

# Example usage: update_max_velocity("123.45")

# the normal button is below
# run_button = tk.Button(window, text="Run", command=run)
# run_button.grid(row=12, column=4, pady=10)

# frame = tk.Frame(window)
# frame.grid(row=5, column=5, columnspan=5, rowspan=5, pady=10)  # Adjust the row and column as needed

# canvas = FigureCanvasTkAgg(pd.process_data(), master=frame)  # Create a canvas for the figure
# canvas.draw()
# canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Pack the canvas into the frame
# canvas.get_tk_widget().config(width=800, height=400)  # Set the canvas size



window.mainloop()