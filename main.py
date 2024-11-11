import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from .src.serial import MicrocontrollerFlasher


# Main GUI application
app = tk.Tk()
app.title("Microcontroller Flasher")
app.geometry("500x550")

# Initialize the MicrocontrollerFlasher class
flasher = MicrocontrollerFlasher(chunk_size=4)

# Port Selection with Dropdown
tk.Label(app, text="Select Serial Port:").pack(pady=5)
port_combo = ttk.Combobox(app)
port_combo.pack()

# Refresh button to reload available ports
def refresh_ports():
    ports = flasher.get_serial_ports()
    port_combo['values'] = [f"{port} - {desc}" for port, desc in ports]
    if ports:
        port_combo.current(0)

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

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin;*.hex")])
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

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
def start_flashing():
    port = port_combo.get().split(" - ")[0]
    baudrate = int(baud_entry.get())
    file_path = file_entry.get()
    start_byte = start_byte_entry.get()
    replace_byte = replace_byte_entry.get()

    if not file_path:
        messagebox.showwarning("Warning", "Please select a file!")
        return

    # Check if start and replace bytes are provided, modify the file if needed
    if start_byte and replace_byte:
        file_path = flasher.modify_file(file_path, start_byte, replace_byte)
        if not file_path:
            return  # Exit if file modification fails

    # Start flashing in a separate thread
    flash_thread = threading.Thread(target=flasher.flash_microcontroller, args=(port, baudrate, file_path))
    flash_thread.start()

    # Start listening for responses in a separate thread
    response_thread = threading.Thread(target=flasher.read_response, args=(port, baudrate, display_text))
    response_thread.daemon = True  # Automatically close with main app
    response_thread.start()

flash_button = tk.Button(app, text="Start Flashing", command=start_flashing)
flash_button.pack(pady=10)

# Data Flow Display
tk.Label(app, text="Data Flow:").pack(pady=5)
display_text = tk.Text(app, height=10, wrap='word')
display_text.pack()

app.mainloop()
