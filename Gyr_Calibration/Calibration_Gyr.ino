#include <Wire.h>
#include <MPU6050.h>
#include <BluetoothSerial.h>

MPU6050 mpu;                // MPU6050 object
BluetoothSerial SerialBT;   // Bluetooth Serial

void setup() {
  Serial.begin(115200);                 // USB serial for debugging
  SerialBT.begin("ESP32_MPU6050");      // Bluetooth name
  Wire.begin();                         // Start I2C communication
  
  // Initialize MPU6050
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed!");
    while (1);
  }
  Serial.println("MPU6050 Initialized.");
}

void loop() {
  int16_t gx, gy, gz;

  // Read raw gyroscope data
  mpu.getRotation(&gx, &gy, &gz);

  // Send raw Gx, Gy, Gz values via Bluetooth and USB serial
  String data = String(gx) + "," + String(gy) + "," + String(gz) + "\n";
  SerialBT.print(data);
  Serial.print(data);

  delay(100);  // Adjust sampling rate
}
