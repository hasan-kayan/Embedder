import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import os

# Function to get all available serial ports and their descriptions
def get_serial_ports():
    ports = list(serial.tools.list_ports.comports())
    return [(port.device, port.description) for port in ports]

# Function to read, replace, and save a modified binary or hex file
def modify_file(file_path, start_byte, replace_byte):
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

# Function to write modified hex/bin data to microcontroller
def flash_microcontroller(port, baudrate, file_path, chunk_size):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    ser.write(data)
                    print(f"Sent {len(data)} bytes to microcontroller.")
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
    port = port_combo.get()
    baudrate = int(baud_entry.get())
    file_path = file_entry.get()
    start_byte = start_byte_entry.get()
    replace_byte = replace_byte_entry.get()
    chunk_size = int(chunk_size_entry.get())

    if not file_path:
        messagebox.showwarning("Warning", "Please select a file!")
        return

    # Check if start and replace bytes are provided, modify the file if needed
    if start_byte and replace_byte:
        file_path = modify_file(file_path, start_byte, replace_byte)
        if not file_path:
            return  # Exit if file modification fails

    # Start flashing in a separate thread
    flash_thread = threading.Thread(target=flash_microcontroller, args=(port, baudrate, file_path, chunk_size))
    flash_thread.start()

    # Start listening for responses in a separate thread
    response_thread = threading.Thread(target=read_response, args=(port, baudrate, display_text))
    response_thread.daemon = True  # Automatically close with main app
    response_thread.start()

def refresh_ports():
    ports = get_serial_ports()
    port_combo['values'] = [f"{port} - {desc}" for port, desc in ports]
    if ports:
        port_combo.current(0)

# Main GUI application
app = tk.Tk()
app.title("Microcontroller Flasher")
app.geometry("500x550")

# Port Selection with Dropdown
tk.Label(app, text="Select Serial Port:").pack(pady=5)
port_combo = ttk.Combobox(app)
port_combo.pack()
refresh_ports()  # Load available ports at startup
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

# Start and Replace Byte Entries
tk.Label(app, text="Start Byte (e.g., BB):").pack(pady=5)
start_byte_entry = tk.Entry(app)
start_byte_entry.pack()

tk.Label(app, text="Replace Byte (e.g., 8080):").pack(pady=5)
replace_byte_entry = tk.Entry(app)
replace_byte_entry.pack()

# Chunk Size Entry
tk.Label(app, text="Bytes per Send (e.g., 4, 8, 16):").pack(pady=5)
chunk_size_entry = tk.Entry(app)
chunk_size_entry.insert(0, "4")  # Default to 4 bytes per send
chunk_size_entry.pack()

# Flash Button
flash_button = tk.Button(app, text="Start Flashing", command=start_flashing)
flash_button.pack(pady=10)

# Data Flow Display
tk.Label(app, text="Data Flow:").pack(pady=5)
display_text = tk.Text(app, height=10, wrap='word')
display_text.pack()

app.mainloop()
