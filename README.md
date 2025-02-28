# MRL-Project
Code for LiDAR Research Project.

Usage Instructions: 

When you have both the LiDAR and ESP32 connected to the computer and note their serial ports do the following. Make sure that you are not actively reading the serial port: 

1. Locate the executable file for the data gathering at /Users/mickelpickle/Documents/GitHub/MRL-Project/rplidar_sdk/output/Darwin/Release/ultra_simple

2. In terminal, write: /Users/mickelpickle/Documents/GitHub/MRL-Project/rplidar_sdk/output/Darwin/Release/ultra_simple --channel --serial  <Lidar Serial Port(either: /dev/tty.usbserial-2 or /dev/tty.usbserial-0001)> <Baudrate (should be 115200)>

3. When prompted, enter arduino serial port and baudrate as such: <Arduino Serial Port (either: /dev/tty.usbserial-2 or /dev/tty.usbserial-0001)> <Baudrate (should be 115200)>

4. Enter the number of seconds and the file name. I like to name files trial# then room then environmental factors. Ex: 2bedroomLightsOn

5. You should see the number of seconds you inputted. When you are finished collecting points, close out of the program (^C)

6. Now process the data by running the "processing.py" script and entering a folder path (use copy path). 

7. Voxelized data will show up in the CSVFiles > voxelized_data and raw data will be in processed_data.