#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

// Calibration coefficients (replace with your values)
float m_x = 0.996, b_x = -0.047; // X-axis calibration
float m_y = 0.997, b_y = -0.010; // Y-axis calibration
float m_z = 0.985, b_z = -0.023; // Z-axis calibration

void setup() {
  Serial.begin(115200);
  Wire.begin();
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed!");
    while (1);
  }
}

void loop() {
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);

  // Convert raw accelerometer data to G's
  float raw_x = ax / 16384.0;
  float raw_y = ay / 16384.0;
  float raw_z = az / 16384.0;

  // Apply calibration
  float calibrated_x = m_x * raw_x + b_x;
  float calibrated_y = m_y * raw_y + b_y;
  float calibrated_z = m_z * raw_z + b_z;

  // Print calibrated values in CSV format
  Serial.print(calibrated_x);
  Serial.print(",");
  Serial.print(calibrated_y);
  Serial.print(",");
  Serial.println(calibrated_z);

  delay(100);
}
