import serial
import time

def calibrate_axis(serial_port, axis_index, calibration_time=5):
    """
    Calibrates the accelerometer for the given axis.

    Parameters:
        serial_port (str): COM port where ESP32 is connected.
        axis_index (int): 0 = X-axis, 1 = Y-axis, 2 = Z-axis.
        calibration_time (int): Duration for each calibration step.

    Returns:
        m (float): Slope.
        b (float): Intercept.
    """
    def prompt_user(message):
        input(f"{message} Press Enter when ready.")

    print(f"Calibrating Axis {axis_index} on port {serial_port}...")
    ser = serial.Serial(serial_port, 115200, timeout=1)
    time.sleep(2)

    x_sum, y_sum, x_squared_sum, xy_sum = 0, 0, 0, 0
    num_points = 0

    # Calibration Step 1: +1g (upwards)
    prompt_user("Place the axis upwards (against gravity).")
    end_time = time.time() + calibration_time
    while time.time() < end_time:
        line = ser.readline().decode().strip()
        if line:
            try:
                accel = [float(v) for v in line.split(",")]
                offset = accel[axis_index] - 1
                x_sum += 1
                y_sum += offset
                x_squared_sum += 1
                xy_sum += offset
                num_points += 1
            except ValueError:
                pass

    # Calibration Step 2: -1g (downwards)
    prompt_user("Place the axis downwards (towards gravity).")
    end_time = time.time() + calibration_time
    while time.time() < end_time:
        line = ser.readline().decode().strip()
        if line:
            try:
                accel = [float(v) for v in line.split(",")]
                offset = accel[axis_index] + 1
                x_sum += -1
                y_sum += offset
                x_squared_sum += 1
                xy_sum += -offset
                num_points += 1
            except ValueError:
                pass

    # Calibration Step 3: 0g (perpendicular)
    prompt_user("Place the axis perpendicular to gravity.")
    end_time = time.time() + calibration_time
    while time.time() < end_time:
        line = ser.readline().decode().strip()
        if line:
            try:
                accel = [float(v) for v in line.split(",")]
                offset = accel[axis_index]
                x_sum += 0
                y_sum += offset
                x_squared_sum += 0
                xy_sum += 0
                num_points += 1
            except ValueError:
                pass

    # Compute m and b using least squares method
    m = (num_points * xy_sum - x_sum * y_sum) / (num_points * x_squared_sum - x_sum**2)
    b = (y_sum - m * x_sum) / num_points

    print(f"Calibration Complete: m = {m:.5f}, b = {b:.5f}")
    ser.close()
    return m, b


if __name__ == "__main__":
    serial_port = "COM4"  # Explicitly set to COM4
    print(f"Using fixed serial port: {serial_port}")
    axis = int(input("Enter the axis to calibrate (0=X, 1=Y, 2=Z): "))
    calibrate_axis(serial_port, axis)
