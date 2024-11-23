from os import path
from sys import exit
import numpy as np
from rplidar import RPLidar
import csv
import serial 
import pandas as pd
import time

#Serial Instance Variable
serialInst = serial.Serial()

#Set the baudrate and port for the code    
serialInst.baudrate = 9600
serialInst.port = '/dev/tty.usbmodem11101'
serialInst.open()
 
BAUD_RATE: int = 115200
TIMEOUT: int = 1

DEVICE_PATH: str = '/dev/tty.usbserial-0001'

D_MAX: int = 5000
I_MIN: int = 0
I_MAX: int = 50 
 
 
def verify_device() -> bool:
    if path.exists(DEVICE_PATH and serialInst.port):
        return True
    else:
        return False
 
 
def run(iterator):
    servo = serialInst.readline()
    scan = next(iterator)
    offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan])
    servoarray = np.array([[int(servo)]])
    servoarray = np.tile(servoarray, len(offsets))
    offsetservo = np.hstack((offsets, servoarray.T))
    df = pd.DataFrame(np.array(offsetservo))
    df.to_csv('points.csv', mode='a', index=True, header=[0,0,0])
    return "Succcessful Scan"
    
with open('points.csv', mode='w', newline='') as csvfile:   
    csv_writer = csv.writer(csvfile, delimiter=',') 

    if __name__ == '__main__':
    
        if not verify_device():
            print(f'No device found: {DEVICE_PATH}')
            exit(1)
    
        lidar = RPLidar(port=DEVICE_PATH, baudrate=BAUD_RATE, timeout=TIMEOUT)
        lidar.start_motor()
        lidar.reset()
    
        while True:
            iterator = lidar.iter_scans()
            run(iterator)
            print(run(iterator))

    csvfile.close()