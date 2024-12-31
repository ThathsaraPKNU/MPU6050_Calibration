import serial
import time

def calibrate_gyroscope(serial_port, calibration_time=10):
    """
    Calibrates the gyroscope by calculating average offsets for Gx, Gy, and Gz.

    Parameters:
        serial_port (str): The port where ESP32 is connected (e.g., "COM3" or "/dev/ttyUSB0").
        calibration_time (int): Duration (seconds) for calibration.

    Returns:
        dict: Dictionary with Gx, Gy, and Gz offsets.
    """
    print("Connecting to ESP32...")
    try:
        ser = serial.Serial(serial_port, 115200, timeout=1)
        time.sleep(2)  # Allow the connection to initialize
        print("Connected to ESP32.\nStarting gyroscope calibration...")

        gx_offset = 0
        gy_offset = 0
        gz_offset = 0
        num_points = 0

        start_time = time.time()
        while time.time() - start_time < calibration_time:
            line = ser.readline().decode('utf-8').strip()
            if line:
                try:
                    # Parse Gx, Gy, Gz data
                    gx, gy, gz = map(int, line.split(','))
                    gx_offset += gx
                    gy_offset += gy
                    gz_offset += gz
                    num_points += 1
                except ValueError:
                    print("Invalid data received, skipping...")

        # Calculate average offsets
        gx_offset /= num_points
        gy_offset /= num_points
        gz_offset /= num_points

        offsets = {"Gx_offset": gx_offset, "Gy_offset": gy_offset, "Gz_offset": gz_offset}

        print("\nCalibration complete! Gyroscope Offsets:")
        print(f"  Gx Offset: {gx_offset:.2f}")
        print(f"  Gy Offset: {gy_offset:.2f}")
        print(f"  Gz Offset: {gz_offset:.2f}")

        ser.close()
        return offsets

    except serial.SerialException as e:
        print("Error:", e)
        return None

def main():
    serial_port = "COM4"  # Replace with your Bluetooth COM port
    calibration_time = 10  # Calibration duration in seconds

    offsets = calibrate_gyroscope(serial_port, calibration_time)
    if offsets:
        print("\nOffsets to apply:")
        print(offsets)
    else:
        print("Calibration failed. Please try again.")

if __name__ == "__main__":
    main()
