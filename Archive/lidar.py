from os import path
from sys import exit
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from rplidar import RPLidar
import csv
import serial 
import pandas as pd

#Serial Instance Variable
serialInst = serial.Serial()

#Set the baudrate and port for the code    
serialInst.baudrate = 9600
serialInst.port = '/dev/tty.usbmodem1101'
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
 
 
def update_line(num, iterator, line):
    servo = serialInst.readline()
    scan = next(iterator)
    offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan])
    line.set_offsets(offsets)
    servoarray = np.array([[int(servo)]])
    servoarray = np.tile(servoarray, len(offsets))
    offsetservo = np.hstack((offsets, servoarray.T))
    df = pd.DataFrame(np.array(offsetservo))
    df.to_csv('points.csv', mode='a', index=True, header=[0,0,0])
    return line
 
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
            plt.rcParams['toolbar'] = 'None'
            fig = plt.figure()
    
            ax = plt.subplot(111, projection='polar')
            line = ax.scatter([0, 0], [0, 0], s=5, c=[I_MIN, I_MAX], cmap=plt.cm.Greys_r, lw=0)
            ax.set_theta_direction(-1)
            ax.set_rmax(D_MAX)
    
            ax.grid(True)
    
            iterator = lidar.iter_scans(max_buf_meas=5000)
            ani = animation.FuncAnimation(fig, update_line, fargs=(iterator, line), interval=50, cache_frame_data=True)
            
            plt.show()
    
        except KeyboardInterrupt:
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
    csvfile.close()