import serial
from rplidar import RPLidar
import csv
import pandas as pd
import numpy as np
from os import path
import time

# Configuration
SERIAL_INPUT_PORT = '/dev/tty.usbmodem1101'  # arduino
INPUT_BAUD_RATE = 9600
BAUD_RATE: int = 115200
TIMEOUT: int = 0.25
DEVICE_PATH: str = '/dev/tty.usbserial-0001' # rplidar
CSV_FILE = 'points.csv'

def verify_device() -> bool:
    return path.exists(DEVICE_PATH) and path.exists(SERIAL_INPUT_PORT)


if __name__ == '__main__':
    verify_device()
    
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
        measurement = lidar.iter_measurments()
        measurement  = list(measurement)
        offsets = np.array([(np.radians(measurement[2]), measurement[3])])
        servoarray = np.array([[int(ser.readline())]])
        offsetservo = np.hstack((offsets, servoarray))
        print(offsetservo)
        df = pd.DataFrame(np.array(offsetservo))
        df.to_csv('points.csv', mode='a', index=True, header=False)  
                                
    except KeyboardInterrupt:
        print("Exiting...")
    #except Exception as e:
     #   print(e)
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