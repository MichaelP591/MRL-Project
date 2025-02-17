#!/usr/bin/env python3
'''Records measurments to a given file. Usage example:


$ ./record_measurments.py out.txt'''
from rplidar import RPLidar
import serial
import asyncio




# Config For Serial
SERIAL_INPUT_PORT = 'COM3'
INPUT_BAUD_RATE = 9600
ser = serial.Serial(SERIAL_INPUT_PORT, INPUT_BAUD_RATE)


#Config for RPLidar
PORT_NAME = 'COM4'


#Input = File to Write To
async def run():
    '''Main function'''
    lidar = RPLidar(PORT_NAME)
    try:
        print('Recording measurments... Press Crl+C to stop.')
        for measurment in lidar.iter_measures():
            if (measurment[1]!=0):
                line = ', '.join(str(v) for v in measurment)
                #line = ', '.join(measurment[2])
                #line = ', '.join(measurment[3])
            yield line
    except KeyboardInterrupt:
        print('Stoping.')
    lidar.stop()
    lidar.disconnect()

async def serialRead(path, input, line):
    outfile = open(path, 'w')
    output = input
    output = ', '.join(line)
    outfile.write(output + '\n')
    outfile.close()


if __name__ == '__main__':
    try: 
        a = asyncio.run(run())
        line = ser.readline().decode('utf-8').strip
        for i in a:
            if ser.in_waiting() != 0:
                line = ser.readline().decode('utf-8').strip
            run(serialRead('points.csv', a, line))
    except Exception:
        print(Exception)
    finally:
        print("Program Closed")
