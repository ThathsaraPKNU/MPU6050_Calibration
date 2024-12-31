#include <Wire.h>
#include <MPU6050.h>
#include <BluetoothSerial.h>

MPU6050 mpu;
BluetoothSerial SerialBT;

// Replace these offsets with the values obtained from calibration
double gx_offset = 786.12;
double gy_offset = -575.46;
double gz_offset = -82.31;

// Low-pass filter variables
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

  // Step 1: Average multiple samples for smoothing
  getAveragedGyro(avg_gx, avg_gy, avg_gz, 20);  // Average over 10 samples

  // Step 2: Apply low-pass filter
  filtered_gx = alpha * avg_gx + (1 - alpha) * filtered_gx;
  filtered_gy = alpha * avg_gy + (1 - alpha) * filtered_gy;
  filtered_gz = alpha * avg_gz + (1 - alpha) * filtered_gz;

  // Step 3: Send filtered data via Bluetooth and Serial Monitor
  String data = String(filtered_gx, 2) + "," + String(filtered_gy, 2) + "," + String(filtered_gz, 2) + "\n";
  SerialBT.print(data);
  Serial.print("Filtered Gyro: ");
  Serial.println(data);

  delay(100);  // Adjust delay for the desired output rate
}
