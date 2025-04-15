import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
for port in ports:

    if (port.description.__contains__("USB2.0-Ser")):
        # Check if the port is a USB serial device
        print(f"Found: {port.device} - {port.description}")
        
        with serial.Serial(port.device, 9600, timeout=0.01) as ser:
            while True:
                #print(f"Listening to serial port: {port.device}")
                data = ser.read(1)  # Read one byte
                if data:
                    print(f"Received data: {data}")  # Debugging output
                if data == b'\xFF':
                    print("Received data packet: 0xFF")

    
