from os import path
import serial
from rplidar import RPLidar
import csv
import pandas as pd
import numpy as np
import time

# Configuration
SERIAL_INPUT_PORT = '/dev/tty.usbmodem1101'  # Replace with your input serial port
INPUT_BAUD_RATE = 9600        # Baud rate for input serial communication

BAUD_RATE: int = 115200
TIMEOUT: int = 0.5
DEVICE_PATH: str = '/dev/tty.usbserial-0001'

def verify_device() -> bool:
    return path.exists(DEVICE_PATH) and path.exists(SERIAL_INPUT_PORT)
    
def main():
    if not verify_device():
        print(f'No device found: {DEVICE_PATH}')
        exit(1)

    # Initialize serial input and RPLidar
    ser = serial.Serial(SERIAL_INPUT_PORT, INPUT_BAUD_RATE)
    lidar = RPLidar(port=DEVICE_PATH, baudrate=BAUD_RATE, timeout=TIMEOUT)

    time.sleep(1)
    print("Starting RPLidar...")

    
    try:
        while True:
            line = int(ser.read(size=4))

            # Perform a new lidar scan
            print("Starting Lidar scan...")
            
            for scan in lidar.iter_scans():
                print(f"Received line: {line}")
                print(f"Scan received: {len(scan)} measurements \n")

                # Process the scan data here
                offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan if len(meas) >= 3])
                servoarray = np.array([[int(line)]])
                servoarray = np.tile(servoarray, len(offsets))
                offsetservo = np.hstack((offsets, servoarray.T))
                df = pd.DataFrame(np.array(offsetservo))
                df.to_csv('points.csv', mode='a', index=True, header=False)
                break
            
            lidar.stop()
            lidar.clean_input()
            ser.read_all()
                        
    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        print("Stopping RPLidar...")
        lidar.stop()
        lidar.disconnect()
        ser.close()

if __name__ == '__main__':
    with open('points.csv', mode='w', newline='') as csvfile:   
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['num', 'angle', 'distance', 'servo'])  

        main()
        csvfile.close()
        print(f"CSV File: {csvfile} is closed.")
        exit()