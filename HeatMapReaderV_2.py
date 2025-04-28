import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
from tkinter import simpledialog, messagebox
import re
import time
import os

# ==================== SETTINGS GUI ====================

def get_parameters():
    param_window = tk.Tk()
    param_window.title("Simulation Parameters")

    entries = {}

    defaults = {
        "Serial Port (e.g., COM3)": "COM3",
        "Baud Rate": "9600",
        "Refresh Interval (ms)": "100",
        "Max Duration (seconds)": "60",
        "Save File Name": "sensor_data",
        "Grid Rows": "4",
        "Grid Columns": "4",
        "Colorbar Min Value": "0",
        "Colorbar Max Value": "5",
    }

    row = 0
    for label_text, default_value in defaults.items():
        label = tk.Label(param_window, text=label_text)
        label.grid(row=row, column=0, sticky="w", padx=5, pady=5)
        entry = tk.Entry(param_window)
        entry.insert(0, default_value)
        entry.grid(row=row, column=1, padx=5, pady=5)
        entries[label_text] = entry
        row += 1

    # Add Data Format Example
    format_label = tk.Label(param_window, text="Expected Data Format:\nV0=1.23V,V1=2.34V,...,Vn=4.56V", fg="blue")
    format_label.grid(row=row, column=0, columnspan=2, padx=5, pady=10)

    def submit():
        for key in defaults.keys():
            defaults[key] = entries[key].get()
        param_window.destroy()

    submit_button = tk.Button(param_window, text="Start Simulation", command=submit)
    submit_button.grid(row=row+1, column=0, columnspan=2, pady=10)

    param_window.mainloop()

    return defaults

# Get parameters
params = get_parameters()

# Parse parameters
SERIAL_PORT = params["Serial Port (e.g., COM3)"]
BAUD_RATE = int(params["Baud Rate"])
REFRESH_INTERVAL = int(params["Refresh Interval (ms)"])
MAX_DURATION_SECONDS = int(params["Max Duration (seconds)"])
SAVE_FILENAME = params["Save File Name"]
GRID_ROWS = int(params["Grid Rows"])
GRID_COLS = int(params["Grid Columns"])
COLOR_MIN = float(params["Colorbar Min Value"])
COLOR_MAX = float(params["Colorbar Max Value"])

NUM_CHANNELS = GRID_ROWS * GRID_COLS

# ==================== SERIAL SETUP ====================
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
ser.flush()

# ==================== DATA STORAGE ====================
start_time = time.monotonic()
elapsed_time = 0
history = [[] for _ in range(NUM_CHANNELS)]
time_stamps = []
turn_count = 0
recording_done = False

# ==================== PLOT SETUP ====================
fig, ax = plt.subplots(figsize=(8, 8))
heatmap = ax.imshow(np.zeros((GRID_ROWS, GRID_COLS)), cmap='viridis', vmin=COLOR_MIN, vmax=COLOR_MAX)
cbar = plt.colorbar(heatmap, ax=ax)
ax.set_title("Real-Time Photoresistor Voltages")
ax.set_xlabel("Columns")
ax.set_ylabel("Rows")

# Add Channel Labels
for i in range(GRID_ROWS):
    for j in range(GRID_COLS):
        channel_num = i * GRID_COLS + j
        ax.text(j, i, f"C{channel_num}", ha="center", va="center", color="white", fontsize=8)

# ==================== FUNCTIONS ====================

def parse_data(line):
    try:
        matches = re.findall(r"V(\d+)=(\d+\.\d)V", line)
        if len(matches) != NUM_CHANNELS:
            print(f"Faulty read: Expected {NUM_CHANNELS} channels, got {len(matches)} channels.")
            return None
        matches.sort(key=lambda x: int(x[0]))  # Sort by channel number
        values = [float(val) for ch, val in matches]
        return values
    except Exception as e:
        print(f"Error parsing line: {e}")
        return None

from tkinter import filedialog

def save_data():
    # Ask user where to save the file
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Save Data As"
    )

    if not file_path:
        print("Save canceled. No data saved.")
        return

    total_turns = min([len(h) for h in history if len(h) > 0], default=0)

    if total_turns == 0:
        print("No valid data to save. Skipping save.")
        return

    print(f"Saving data to {file_path}...")
    with open(file_path, 'w', newline='') as f:
        header = "Turn,Timestamp (s)," + ",".join([f"C{i}" for i in range(NUM_CHANNELS)])
        f.write(header + "\n")
        for idx in range(total_turns):
            row = [str(idx)]
            row.append(f"{time_stamps[idx]:.2f}" if idx < len(time_stamps) else '')
            for ch in range(NUM_CHANNELS):
                value = history[ch][idx] if idx < len(history[ch]) else ''
                row.append(str(value))
            f.write(",".join(row) + "\n")
    print("Data saved successfully!")


def update(frame):
    global turn_count, elapsed_time, recording_done

    if recording_done:
        return

    elapsed_time = time.monotonic() - start_time

    if elapsed_time >= MAX_DURATION_SECONDS:
        print(f"Max time ({MAX_DURATION_SECONDS}s) reached. Stopping...")
        ser.close()
        save_data()
        print("Recording finished. Graph will stay open. Close manually when done.")
        recording_done = True
        return

    if ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8').strip()
            print(line)
            values = parse_data(line)

            if values is not None:
                # Update history
                for i in range(NUM_CHANNELS):
                    history[i].append(values[i])

                time_stamps.append(elapsed_time)
                turn_count += 1

                # Update heatmap
                data = np.array(values).reshape((GRID_ROWS, GRID_COLS))
                heatmap.set_data(data)
                heatmap.set_clim(vmin=COLOR_MIN, vmax=COLOR_MAX)

        except Exception as e:
            print(f"Serial read error: {e}")

ani = animation.FuncAnimation(fig, update, interval=REFRESH_INTERVAL)
plt.tight_layout()
plt.show()
