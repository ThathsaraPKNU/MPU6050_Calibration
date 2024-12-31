#include <Wire.h>
#include <MPU6050.h>
#include <BluetoothSerial.h>

MPU6050 mpu;
BluetoothSerial SerialBT;

// Gyroscope calibration offsets
double gx_offset = 776.29;
double gy_offset = -570.65;
double gz_offset = -83.47;

// Accelerometer calibration coefficients (replace with your values)
float m_x = 0.996, b_x = -0.047; // X-axis
float m_y = 0.997, b_y = -0.010; // Y-axis
float m_z = 0.985, b_z = -0.023; // Z-axis

// Low-pass filter variables for gyroscope
double filtered_gx = 0, filtered_gy = 0, filtered_gz = 0;
double alpha = 0.3;  // Low-pass filter strength (0 < alpha <= 1)

// Function to get averaged gyroscope values
void getAveragedGyro(double &avg_gx, double &avg_gy, double &avg_gz, int samples) {
  int16_t gx, gy, gz;
  avg_gx = 0;
  avg_gy = 0;
  avg_gz = 0;

  for (int i = 0; i < samples; i++) {
    mpu.getRotation(&gx, &gy, &gz);
    avg_gx += gx - gx_offset;  // Apply offsets
    avg_gy += gy - gy_offset;
    avg_gz += gz - gz_offset;
    delay(10);  // Small delay between samples
  }

  avg_gx /= samples;  // Average the samples
  avg_gy /= samples;
  avg_gz /= samples;
}

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32_MPU6050");  // Bluetooth name
  Wire.begin();

  // Initialize MPU6050
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed!");
    while (1);
  }
  Serial.println("MPU6050 Initialized.");
}

void loop() {
  double avg_gx, avg_gy, avg_gz;
  int16_t ax, ay, az;

  // Step 1: Average multiple gyroscope samples for smoothing
  getAveragedGyro(avg_gx, avg_gy, avg_gz, 20);  // Average over 20 samples

  // Step 2: Apply low-pass filter to gyroscope values
  filtered_gx = alpha * avg_gx + (1 - alpha) * filtered_gx;
  filtered_gy = alpha * avg_gy + (1 - alpha) * filtered_gy;
  filtered_gz = alpha * avg_gz + (1 - alpha) * filtered_gz;

  // Step 3: Get raw accelerometer values
  mpu.getAcceleration(&ax, &ay, &az);

  // Convert raw accelerometer data to G's and apply calibration
  float raw_accel_x = ax / 16384.0;
  float raw_accel_y = ay / 16384.0;
  float raw_accel_z = az / 16384.0;

  float calibrated_accel_x = m_x * raw_accel_x + b_x;
  float calibrated_accel_y = m_y * raw_accel_y + b_y;
  float calibrated_accel_z = m_z * raw_accel_z + b_z;

  // Step 4: Combine all values and send them via Bluetooth and Serial Monitor
  String data = String(calibrated_accel_x, 2) + "," + 
                String(calibrated_accel_y, 2) + "," + 
                String(calibrated_accel_z, 2) + "," +
                String(filtered_gx, 2) + "," + 
                String(filtered_gy, 2) + "," + 
                String(filtered_gz, 2) + "\n";

  SerialBT.print(data);
  Serial.print("Ax, Ay, Az, Gx, Gy, Gz: ");
  Serial.println(data);

  delay(100);  // Adjust delay for the desired output rate
}
