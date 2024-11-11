import serial
import serial.tools.list_ports
import threading
import time
import os
from tkinter import messagebox

class MicrocontrollerFlasher:
    def __init__(self, chunk_size=4):
        self.chunk_size = chunk_size

    def get_serial_ports(self):
        """Get all available serial ports and their descriptions."""
        ports = list(serial.tools.list_ports.comports())
        return [(port.device, port.description) for port in ports]

    def modify_file(self, file_path, start_byte, replace_byte):
        """Read, replace, and save a modified binary or hex file."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            # Replace occurrences of the start_byte with replace_byte
            modified_data = data.replace(bytes.fromhex(start_byte), bytes.fromhex(replace_byte))

            # Save the modified file to the desktop
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            new_file_path = os.path.join(desktop_path, f"modified_{os.path.basename(file_path)}")
            with open(new_file_path, 'wb') as new_file:
                new_file.write(modified_data)

            print(f"Modified file saved as {new_file_path}")
            messagebox.showinfo("Info", f"Modified file saved to Desktop: {new_file_path}")
            return new_file_path  # Return the path to use in flashing
        except Exception as e:
            print(f"Error in modifying file: {e}")
            messagebox.showerror("Error", f"Failed to modify file: {e}")
            return None

    def flash_microcontroller(self, port, baudrate, file_path):
        """Write modified hex/bin data to microcontroller."""
        try:
            with serial.Serial(port, baudrate, timeout=1) as ser:
                with open(file_path, 'rb') as f:
                    while True:
                        data = f.read(self.chunk_size)
                        if not data:
                            break
                        ser.write(data)
                        print(f"Sent {len(data)} bytes to microcontroller.")
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", f"Failed to flash microcontroller: {e}")

    def read_response(self, port, baudrate, display_text):
        """Handle UART response from the microcontroller."""
        try:
            with serial.Serial(port, baudrate, timeout=1) as ser:
                while True:
                    if ser.in_waiting > 0:
                        response = ser.readline().decode('utf-8').strip()
                        if response:
                            display_text.insert('end', f"Response: {response}\n")
                            display_text.see('end')
                    time.sleep(0.1)
        except Exception as e:
            print(f"Error: {e}")
