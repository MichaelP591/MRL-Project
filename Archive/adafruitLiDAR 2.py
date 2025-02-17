import serial
from adafruit_rplidar import RPLidar
import csv
import pandas as pd
import numpy as np
import time

# Configuration
SERIAL_INPUT_PORT = '/dev/tty.usbmodem101'  # arduino
INPUT_BAUD_RATE = 9600
BAUD_RATE: int = 115200
TIMEOUT: int = 1
DEVICE_PATH: str = '/dev/tty    .usbserial-0001' # rplidar
CSV_FILE = 'points.csv'

# Setup the RPLidar
PORT_NAME = '/dev/tty.usbserial-0001'
lidar = RPLidar(None, PORT_NAME, timeout=1)

# Setup Serial Port
ser = serial.Serial(SERIAL_INPUT_PORT, INPUT_BAUD_RATE)

def process_data(a, d, s):
    offsets = np.array[[(np.radians(a), d, int(s))]]
    servoarray = np.array([[int(ser.readline())]])
    offsetservo = np.hstack((offsets, servoarray))
    print(offsetservo)
    df = pd.DataFrame(np.array(offsetservo))
    df.to_csv('points.csv', mode='a', index=True, header=False) 


def main():
    try:
        #    print(lidar.get_info())
        for scan in lidar.iter_scans():
            servo = ser.readline()
            for _, angle, distance in scan:
                #process_data(angle, distance, servo)
                print(f'Angle: {angle:.2f}°, Distance: {distance:.2f} cm')
            

    except KeyboardInterrupt:
        print("Stopping.")
    lidar.stop()
    lidar.disconnect()

if __name__ == '__main__':
    with open('points.csv', mode='w', newline='') as csvfile:   
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['num', 'angle', 'distance', 'servo'])  

        main()
        csvfile.close()
        print(f"CSV File: {csvfile} is closed.")
        exit()