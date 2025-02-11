// Code for rotating a servo and gathering IMU data and printing it to the serial 

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <ESP32Servo.h>

unsigned long lastTime = 0;
float yaw = 0;  
float vX = 0;
float vY = 0;
float vZ = 0;
const long delayTime = 1;

Adafruit_MPU6050 mpu;
Servo servo;

// Don't worry about anything in the setup function it is mainly used for setting up the IMU range and other things
void setup(void) {
  int servoOutput = servo.attach(18);

  Serial.begin(115200);
  Serial.println(servoOutput);
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  Serial.println("Adafruit MPU6050 test!");

  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  Serial.print("Accelerometer range set to: ");
  switch (mpu.getAccelerometerRange()) {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.print("Gyro range set to: ");
  switch (mpu.getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }

  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (mpu.getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }

  Serial.println("");
  delay(100);
  lastTime = millis();  // Initialize time for integration
}

void loop() {
  // the loop function simply rotates the servo from 0 to 180 degrees and then back again

  for (int i = 0; i < 180; i++) {
    servo.write(map(i, 0, 270, 0, 180)); // map function used due to the 270 degree servo
    gatherIMU(); //imu data
    delay(delayTime);
  }
  for (int i = 180; i >= 0; i--) {
    servo.write(map(i, 0, 270, 0, 180));
    gatherIMU();
    delay(delayTime);
  }
}

void gatherIMU() {

  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  float accelX = a.acceleration.x;
  float accelY = a.acceleration.y;
  float accelZ = a.acceleration.z;
  float roll  = atan2(accelY, accelZ) * 180 / PI;
  float pitch = atan2(-accelX, sqrt(accelY * accelY + accelZ * accelZ)) * 180 / PI;

  // Compute yaw by integrating gyroscope Z-axis
  unsigned long currentTime = millis();
  float dt = (currentTime - lastTime) / 1000.0;  // Convert ms to seconds
  lastTime = currentTime;

  /* 
   * JAAAAAAAMMMMMMMESSS!!!!!!!!! 
   * these four values will have IMU integration drift and right now Vx, Vy, and Vz all 
   * are only giving velocity and not distance. Come up with a filter to try and remove
   * some of the drift from the IMU. Look into kalman filters as they are really common
   * in this field.  Also, print out all of the values as follows (Dx, Dy, Dz; Roll, Pitch, Yaw)
   * you better actually do something or else ill smack you james.
   */
  vX += accelX * dt;
  vY += accelY * dt;
  vZ += accelZ * dt;
  yaw += g.gyro.z * dt;  // Integrate gyroscope Z data

  // Output roll, pitch, yaw in CSV format
  Serial.print(roll);
  Serial.print(",");
  Serial.print(pitch);
  Serial.print(",");
  Serial.println(yaw);

  // You probably don't need this but just to show that te IMU can measure temperature
  /*Serial.print("Temperature: ");
  Serial.print(temp.temperature);
  Serial.println(" degC"); */
}
