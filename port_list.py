import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
for port in ports:

    if (port.description.__contains__("USB2.0-Ser")):
        # Check if the port is a USB serial device
        print(f"Found: {port.device} - {port.description}")