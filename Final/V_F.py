import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import serial
from math import atan2, sqrt, pi

# Serial Port Configuration
SERIAL_PORT = "COM4"  # Replace with your ESP32's port
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Connected to ESP32")
except Exception as e:
    print(f"Error connecting to serial port: {e}")
    exit()

# Accelerometer and Gyroscope data
accel_x = accel_y = accel_z = 0.0
gyro_x = gyro_y = gyro_z = 0.0

# Smoothed pitch and roll
smooth_pitch = smooth_roll = 0.0
alpha = 0.2  # Low-pass filter strength (0 < alpha <= 1)

def resize(width, height):
    if height == 0: height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

def draw_plate():
    """Draw a 3D rectangular plate."""
    w, h, t = 2.0, 1.0, 0.2  # Width, Height, Thickness

    glBegin(GL_QUADS)

    # Top face (Blue)
    glColor3f(0.2, 0.5, 0.8)
    glVertex3f(-w / 2, -h / 2, t / 2)
    glVertex3f(w / 2, -h / 2, t / 2)
    glVertex3f(w / 2, h / 2, t / 2)
    glVertex3f(-w / 2, h / 2, t / 2)

    # Bottom face (Red)
    glColor3f(0.8, 0.2, 0.2)
    glVertex3f(-w / 2, -h / 2, -t / 2)
    glVertex3f(w / 2, -h / 2, -t / 2)
    glVertex3f(w / 2, h / 2, -t / 2)
    glVertex3f(-w / 2, h / 2, -t / 2)

    glEnd()

def read_serial_data():
    global accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z
    try:
        line = ser.readline().decode("utf-8").strip()
        print(f"Raw data: {line}")  # Debug raw data

        # Remove labels and parse data
        if line.startswith("Ax, Ay, Az, Gx, Gy, Gz:"):
            values = line.replace("Ax, Ay, Az, Gx, Gy, Gz: ", "").split(",")
            if len(values) == 6:  # Ensure all 6 values are received
                accel_x, accel_y, accel_z = map(float, values[:3])
                gyro_x, gyro_y, gyro_z = map(float, values[3:])
                print(f"Accel: ({accel_x}, {accel_y}, {accel_z}), Gyro: ({gyro_x}, {gyro_y}, {gyro_z})")  # Debug parsed values
    except Exception as e:
        print(f"Error reading serial data: {e}")

def render():
    global accel_x, accel_y, accel_z, smooth_pitch, smooth_roll  # Declare globals

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0.0, -7)  # Move back the plate for a better view

    # Calculate pitch and roll based on accelerometer data
    raw_pitch = atan2(accel_y, sqrt(accel_x**2 + accel_z**2)) * 180 / pi
    raw_roll = atan2(-accel_x, sqrt(accel_y**2 + accel_z**2)) * 180 / pi

    # Smooth pitch and roll using a low-pass filter
    smooth_pitch = alpha * raw_pitch + (1 - alpha) * smooth_pitch
    smooth_roll = alpha * raw_roll + (1 - alpha) * smooth_roll

    # Debug: Print current pitch and roll
    print(f"Raw Pitch: {raw_pitch}, Raw Roll: {raw_roll}")
    print(f"Smoothed Pitch: {smooth_pitch}, Smoothed Roll: {smooth_roll}")

    # Apply rotations
    glRotatef(-smooth_pitch, 1, 0, 0)  # Rotate by pitch (X-axis)
    glRotatef(-smooth_roll, 0, 1, 0)   # Rotate by roll (Y-axis)

    draw_plate()
    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("MPU6050 Plate Visualization")
    resize(800, 600)
    init_opengl()
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        read_serial_data()
        render()
        clock.tick(60)

    ser.close()
    pygame.quit()

if __name__ == "__main__":
    main()
