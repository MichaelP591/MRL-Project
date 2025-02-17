# MRL-Project
Code for LiDAR Research Project.

Usage Instructions: 

When you have both the LiDAR and ESP32 connected to the computer and note their serial ports do the following. Make sure that you are not actively reading the serial port: 

1. Locate the executable file for the data gathering at /Users/mickelpickle/Documents/GitHub/MRL-Project/rplidar_sdk/output/Darwin/Release/ultra_simple

2. In terminal, write: /Users/mickelpickle/Documents/GitHub/MRL-Project/rplidar_sdk/output/Darwin/Release/ultra_simple --channel --serial  <Lidar Serial Port> <Baudrate (should be 115200)>

3. When prompted, enter arduino serial port and baudrate as such: <Arduino Serial Port> <Baudrate (should be 115200)>

4. You should see imu data being outputted in the terminal. When you are finished collecting points, close out of the program (^C)

5. Now process the data by running the "processing.py" script. 

6. The points3d.csv file will have your final points.