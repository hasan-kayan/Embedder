import serial
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import serial.tools.list_ports

# Function to list available serial ports
def list_serial_ports():
    ports = list(serial.tools.list_ports.comports())
    port_list = []
    for port in ports:
        device_info = f"{port.device} - {port.description}"
        port_list.append(device_info)
    return port_list

# Function to write hex/bin data to microcontroller
def flash_microcontroller(port, baudrate, file_path, bytes_to_send):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            with open(file_path, 'rb') as f:
                data = f.read()
                for i in range(0, len(data), bytes_to_send):
                    ser.write(data[i:i + bytes_to_send])
                    time.sleep(0.05)  # Small delay to simulate real communication
                print("Data sent to microcontroller.")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Failed to flash microcontroller: {e}")

# Function to handle UART response from the microcontroller
def read_response(port, baudrate, display_text):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            while True:
                if ser.in_waiting > 0:
                    response = ser.readline().decode('utf-8').strip()
                    if response:
                        display_text.insert(tk.END, f"Response: {response}\n")
                        display_text.see(tk.END)
                time.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}")

# GUI setup
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin;*.hex")])
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

def start_flashing():
    port_info = port_var.get()
    port = port_info.split(" - ")[0]  # Extract port name from selection
    baudrate = int(baud_entry.get())
    file_path = file_entry.get()
    bytes_to_send = int(byte_entry.get())
    
    if not file_path:
        messagebox.showwarning("Warning", "Please select a file!")
        return

    # Start flashing in a separate thread
    flash_thread = threading.Thread(target=flash_microcontroller, args=(port, baudrate, file_path, bytes_to_send))
    flash_thread.start()

    # Start listening for responses in a separate thread
    response_thread = threading.Thread(target=read_response, args=(port, baudrate, display_text))
    response_thread.daemon = True  # Automatically close with main app
    response_thread.start()

# Refresh the serial ports list
def refresh_ports():
    port_menu['values'] = list_serial_ports()

# Main GUI application
app = tk.Tk()
app.title("Microcontroller Flasher")
app.geometry("500x500")

# Port selection dropdown
tk.Label(app, text="Select Serial Port:").pack(pady=5)
port_var = tk.StringVar()
port_menu = ttk.Combobox(app, textvariable=port_var, width=40)
port_menu.pack()
port_menu['values'] = list_serial_ports()  # Populate with available ports
refresh_button = tk.Button(app, text="Refresh Ports", command=refresh_ports)
refresh_button.pack(pady=5)

# Baud Rate Entry
tk.Label(app, text="Baud Rate:").pack(pady=5)
baud_entry = tk.Entry(app)
baud_entry.insert(0, "115200")  # Default baud rate
baud_entry.pack()

# File Selection
tk.Label(app, text="Select Hex/Bin File:").pack(pady=5)
file_entry = tk.Entry(app, width=40)
file_entry.pack()
file_button = tk.Button(app, text="Browse", command=open_file)
file_button.pack()

# Byte Send Entry
tk.Label(app, text="Bytes to Send at Once (4, 8, or 16):").pack(pady=5)
byte_entry = tk.Entry(app)
byte_entry.insert(0, "4")  # Default is 4 bytes
byte_entry.pack()

# Flash Button
flash_button = tk.Button(app, text="Start Flashing", command=start_flashing)
flash_button.pack(pady=10)

# Data Flow Display
tk.Label(app, text="Data Flow:").pack(pady=5)
display_text = tk.Text(app, height=10, wrap='word')
display_text.pack()

app.mainloop()
