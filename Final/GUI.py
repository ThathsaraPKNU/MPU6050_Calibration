import serial
import time
import math
import tkinter as tk
from tkinter import ttk

# ------------------------------------------------------------------
# 1) Serial Port Configuration
# ------------------------------------------------------------------
SERIAL_PORT = "COM4"    # <-- Change to your Bluetooth COM port
BAUD_RATE = 115200
GRAVITY = 9.80665       # for converting G to m/s^2
DEG_TO_RAD = math.pi / 180.0  # for converting deg/s to rad/s

# ------------------------------------------------------------------
# 2) Create the Main Window
# ------------------------------------------------------------------
root = tk.Tk()
root.title("ESP32 MPU6050 Monitor")

# Optionally, set a minimum size or geometry:
# root.geometry("450x300")

# Use a style for ttk widgets (optional, for a cleaner look)
style = ttk.Style()
style.theme_use("clam")  # or "default", "vista", etc.
style.configure("TLabelFrame", font=("Helvetica", 12, "bold"), padding=10)
style.configure("TLabel", font=("Helvetica", 12))

# ------------------------------------------------------------------
# 3) Create Three Labeled Frames
# ------------------------------------------------------------------
frame_accel = ttk.LabelFrame(root, text="Acceleration (m/s²)")
frame_gyro  = ttk.LabelFrame(root, text="Gyroscope (rad/s)")
frame_angle = ttk.LabelFrame(root, text="Angles (°)")

frame_accel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
frame_gyro.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
frame_angle.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Make the columns/rows expand with window resizing (optional)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

# ------------------------------------------------------------------
# 4) Labels Within Each Frame
# ------------------------------------------------------------------
# -- Acceleration labels
label_ax = ttk.Label(frame_accel, text="Ax: 0.00")
label_ay = ttk.Label(frame_accel, text="Ay: 0.00")
label_az = ttk.Label(frame_accel, text="Az: 0.00")

label_ax.pack(anchor="w", pady=2)
label_ay.pack(anchor="w", pady=2)
label_az.pack(anchor="w", pady=2)

# -- Gyroscope labels (in rad/s)
label_gx = ttk.Label(frame_gyro, text="Gx: 0.00")
label_gy = ttk.Label(frame_gyro, text="Gy: 0.00")
label_gz = ttk.Label(frame_gyro, text="Gz: 0.00")

label_gx.pack(anchor="w", pady=2)
label_gy.pack(anchor="w", pady=2)
label_gz.pack(anchor="w", pady=2)

# -- Angles (in degrees)
label_roll  = ttk.Label(frame_angle, text="Roll: 0.00")
label_pitch = ttk.Label(frame_angle, text="Pitch: 0.00")
label_yaw   = ttk.Label(frame_angle, text="Yaw: 0.00")

label_roll.pack(anchor="w", pady=2)
label_pitch.pack(anchor="w", pady=2)
label_yaw.pack(anchor="w", pady=2)

# ------------------------------------------------------------------
# 5) Open the Serial Port
# ------------------------------------------------------------------
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Opened {SERIAL_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"Could not open port {SERIAL_PORT}: {e}")
    ser = None

# ------------------------------------------------------------------
# 6) Periodic Data Read Function
# ------------------------------------------------------------------
def update_data():
    if ser and ser.in_waiting > 0:
        # Read one line, decode, strip whitespace
        line = ser.readline().decode("utf-8", errors="replace").strip()
        print("RAW DATA:", line)

        # If your ESP32 code prints:
        #  "Ax, Ay, Az, Gx, Gy, Gz: 0.02, -0.01, 1.01, 1.26, -0.65, -0.83"
        # Remove that prefix in Python:
        prefix = "Ax, Ay, Az, Gx, Gy, Gz: "
        if line.startswith(prefix):
            line = line[len(prefix):]  # now "0.02, -0.01, 1.01, 1.26, -0.65, -0.83"

        # Split by commas -> should be 6 parts: [Ax_g, Ay_g, Az_g, Gx_deg, Gy_deg, Gz_deg]
        parts = line.split(',')
        if len(parts) == 6:
            try:
                # Parse each as a float
                ax_g = float(parts[0])
                ay_g = float(parts[1])
                az_g = float(parts[2])
                gx_deg = float(parts[3])  # in deg/s
                gy_deg = float(parts[4])  # in deg/s
                gz_deg = float(parts[5])  # in deg/s

                # Convert accelerations: G -> m/s^2
                ax_ms2 = ax_g * GRAVITY
                ay_ms2 = ay_g * GRAVITY
                az_ms2 = az_g * GRAVITY

                # Convert gyro: deg/s -> rad/s
                gx_rad = gx_deg * DEG_TO_RAD
                gy_rad = gy_deg * DEG_TO_RAD
                gz_rad = gz_deg * DEG_TO_RAD

                # Update Accel GUI
                label_ax.config(text=f"Ax: {ax_ms2:.2f}")
                label_ay.config(text=f"Ay: {ay_ms2:.2f}")
                label_az.config(text=f"Az: {az_ms2:.2f}")

                # Update Gyro GUI
                label_gx.config(text=f"Gx: {gx_rad:.2f}")
                label_gy.config(text=f"Gy: {gy_rad:.2f}")
                label_gz.config(text=f"Gz: {gz_rad:.2f}")

                # Simple Roll/Pitch in degrees from accelerometer
                roll_deg  = math.degrees(math.atan2(ay_ms2, az_ms2))
                pitch_deg = math.degrees(math.atan2(-ax_ms2, 
                                    math.sqrt(ay_ms2**2 + az_ms2**2)))
                yaw_deg   = 0.0  # real yaw needs magnetometer or integrated gyro

                label_roll.config(text=f"Roll: {roll_deg:.2f}")
                label_pitch.config(text=f"Pitch: {pitch_deg:.2f}")
                label_yaw.config(text=f"Yaw: {yaw_deg:.2f}")

            except ValueError:
                print("Parsing error: could not convert data to float.")

    # Schedule next update in 100 ms
    root.after(100, update_data)

# ------------------------------------------------------------------
# 7) Start the Periodic Read & GUI
# ------------------------------------------------------------------
update_data()
root.mainloop()
