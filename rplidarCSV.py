from os import path
from sys import exit
import numpy as np
from rplidar import RPLidar
import csv
import serial
import pandas as pd
from datetime import datetime

#Serial Instance Variable
serialInst = serial.Serial()

#Set the baudrate and port for the code    
serialInst.baudrate = 9600
serialInst.port = '/dev/tty.usbmodem11101'
serialInst.open()
 
#RPLidar baudrate and port
BAUD_RATE: int = 115200
TIMEOUT: int = 1
DEVICE_PATH: str = '/dev/tty.usbserial-0001'
 
def verify_device() -> bool:
    if path.exists(DEVICE_PATH):
        return True
    else:
        return False
 
 
def update_line(iterator, servo):
    scan = next(iterator)
    offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan])
    servoarray = np.array([[int(servo)]])
    servoarray = np.tile(servoarray, len(offsets))
    offsetservo = np.hstack((offsets, servoarray.T))
    df = pd.DataFrame(np.array(offsetservo))
    df.to_csv('points.csv', mode='a')
    print(offsetservo)

 
with open('points.csv', mode='w', newline='') as csvfile:   
    csv_writer = csv.writer(csvfile, delimiter=',')
    csv_writer.writerow(['num', 'angle', 'distance', 'servo'])    
    if __name__ == '__main__':
    
        if path.exists(DEVICE_PATH):
 
            print(f'Found RPLidar on path: {DEVICE_PATH}')
    
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    
            print(f'Date and time: {dt_string}')
    
            lidar = RPLidar(port=DEVICE_PATH, baudrate=BAUD_RATE, timeout=TIMEOUT)
    
            info = lidar.get_info()
            for key, value in info.items():
                print(f'{key.capitalize()}: {value}')
    
            health = lidar.get_health()
            print(f'Health: {health}')
    
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
    else:
        print(f'No device found for: {DEVICE_PATH}')
    csvfile.close()
    serialInst.close()