from os import path
from sys import exit
import numpy as np
from rplidar import RPLidar
import csv
import serial 
import pandas as pd

#Serial Instance Variable
serialInst = serial.Serial()

#Set the baudrate and port for the code    
serialInst.baudrate = 9600
serialInst.port = 'COM3'
serialInst.open()
 
#RPLidar baudrate and port
BAUD_RATE: int = 115200
TIMEOUT: int = 1
DEVICE_PATH: str = 'COM4'
 
def verify_device() -> bool:
    if path.exists(DEVICE_PATH):
        return True
    else:
        return False
 
 
def update_line(iterator):
    servo = serialInst.readline()
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
    
        if not verify_device():
            print(f'No device found: {DEVICE_PATH}')
            exit(1)
    
        lidar = RPLidar(port=DEVICE_PATH, baudrate=BAUD_RATE, timeout=TIMEOUT)
        lidar.start_motor()
    
        try:
            iterator = lidar.iter_scans(max_buf_meas=500)
            while True:
                if serialInst.readable():
                    update_line(iterator)
                else:
                    print('No data from servo.')
    
        except KeyboardInterrupt:
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
    csvfile.close()
    serialInst.close()