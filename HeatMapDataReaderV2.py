import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
from tkinter import filedialog, Button, Label
import matplotlib

matplotlib.use('TkAgg')  # Ensures Tkinter backend is active for buttons

# ========= FILE PICKER =========
root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(
    title="Select the CSV data file",
    filetypes=[("CSV Files", "*.csv")]
)

if not file_path:
    print("No file selected. Exiting...")
    exit()

# ========= LOAD DATA =========
print(f"Loading file: {file_path}")

try:
    data = pd.read_csv(file_path)
    print("File loaded successfully!")
except Exception as e:
    print(f"Failed to load file: {e}")
    exit()

print("\nFirst few rows of the file:")
print(data.head())

# ========= DETECT COLUMNS =========
try:
    timestamps = data['Timestamp (s)']
except KeyError:
    print("Error: 'Timestamp (s)' column missing!")
    exit()

channel_columns = [col for col in data.columns if col.startswith('C')]
if not channel_columns:
    print("Error: No channel columns (C0, C1, etc.) found!")
    exit()

print(f"Found {len(channel_columns)} channels: {channel_columns}")

channel_data = data[channel_columns]
num_channels = len(channel_columns)

# ========= GUESS GRID =========
def guess_grid(n):
    for i in range(int(n**0.5), 0, -1):
        if n % i == 0:
            return (i, n // i)
    return (n, 1)

grid_rows, grid_cols = guess_grid(num_channels)
print(f"Guessed grid: {grid_rows} rows x {grid_cols} columns")

# ========= PLOT 1: AVERAGE HEATMAP =========
avg_values = channel_data.mean().values.reshape((grid_rows, grid_cols))

fig1, ax1 = plt.subplots(figsize=(6, 6))
heatmap1 = ax1.imshow(avg_values, cmap='plasma', vmin=0, vmax=5)
plt.colorbar(heatmap1, ax=ax1)
ax1.set_title(f"Averaged Voltages ({grid_rows}x{grid_cols})")
ax1.set_xlabel("Columns")
ax1.set_ylabel("Rows")

for i in range(grid_rows):
    for j in range(grid_cols):
        ch_num = i * grid_cols + j
        ax1.text(j, i, f"C{ch_num}", ha="center", va="center", color="white", fontsize=8)

fig1.tight_layout()

# ========= PLOT 2: TIME SERIES =========
fig2, ax2 = plt.subplots(figsize=(10, 6))
colors = plt.cm.tab20(np.linspace(0, 1, num_channels))

for idx, ch in enumerate(channel_columns):
    ax2.plot(timestamps, channel_data[ch], label=ch, color=colors[idx])

ax2.set_title('Channel Voltages Over Full Time')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Voltage (V)')
ax2.legend(ncol=4, fontsize="small")
ax2.grid(True)

fig2.tight_layout()

# ========= PLOT 3: INTERACTIVE REPLAY =========
current_frame = [0]  # Using a list so we can mutate inside button callbacks

fig3, ax3 = plt.subplots(figsize=(6, 6))
heatmap_replay = ax3.imshow(np.zeros((grid_rows, grid_cols)), cmap='viridis', vmin=0, vmax=5)
cbar = plt.colorbar(heatmap_replay, ax=ax3)
title_text = ax3.set_title(f"Time = {timestamps.iloc[0]:.2f} s")
ax3.set_xlabel("Columns")
ax3.set_ylabel("Rows")

fig3.tight_layout()

# ========= TKINTER WINDOW FOR CONTROLS =========
control_window = tk.Tk()
control_window.title("Replay Controls")
# Seconds per click Entry
seconds_per_click_label = Label(control_window, text="Seconds per Click:")
seconds_per_click_label.grid(row=2, column=0, pady=5)

seconds_per_click_entry = tk.Entry(control_window)
seconds_per_click_entry.insert(0, "1")  # Default to 1 second per click
seconds_per_click_entry.grid(row=2, column=1, pady=5)


def update_frame(delta):
    try:
        seconds_per_click = float(seconds_per_click_entry.get())
    except ValueError:
        seconds_per_click = 1  # default fallback if invalid input

    # Calculate how many frames that means
    if len(timestamps) > 1:
        average_dt = (timestamps.iloc[-1] - timestamps.iloc[0]) / (len(timestamps) - 1)
        frames_to_jump = int(seconds_per_click / average_dt)
    else:
        frames_to_jump = 1

    if frames_to_jump < 1:
        frames_to_jump = 1

    current_frame[0] += delta * frames_to_jump
    current_frame[0] = max(0, min(current_frame[0], len(data)-1))  # Stay inside bounds

    values = channel_data.iloc[current_frame[0]].values.reshape((grid_rows, grid_cols))
    heatmap_replay.set_data(values)
    title_text.set_text(f"Time = {timestamps.iloc[current_frame[0]]:.2f} s")
    fig3.canvas.draw_idle()


Button(control_window, text="Previous", command=lambda: update_frame(-1), width=10).grid(row=0, column=0, padx=10, pady=10)
Button(control_window, text="Next", command=lambda: update_frame(1), width=10).grid(row=0, column=1, padx=10, pady=10)

Label(control_window, text="Use 'Previous' and 'Next' to navigate time").grid(row=1, column=0, columnspan=2, pady=5)

# Start with first frame visible
update_frame(0)

# ========= SHOW EVERYTHING =========
plt.show()
control_window.mainloop()
