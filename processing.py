import serial.tools.list_ports
import math
import csv

#Serial Instance Variable
serialInst = serial.Serial()

#Set the baudrate and port for the code    
serialInst.baudrate = 115200
serialInst.port = '/dev/cu.usbmodem143101'
serialInst.open()

# Convert polar coordinates into standard coordinates
def polarLinear(position, angle):
    list = []
    x = position * math.cos((angle * math.pi)/180)
    y = position * math.sin((angle * math.pi)/180)
    list.append(x); list.append(y)
    return list

#create csv file to write to
with open('points.csv', mode='w') as csvfile:
	csv_writer = csv.writer(csvfile, delimiter=',')
	csv_writer.writerow(['xvals', 'yvals'])
	while True:
		#Read each line and process it
		if serialInst.in_waiting:
			packet = serialInst.readline()
			point = packet.decode('UTF-8').rstrip('\n')
			print(point)
			pointSplit = point.split()
			distance = float(pointSplit[0])
			angle = float(pointSplit[1])
			if (distance > 150.0 and distance < 100000):
				xy = polarLinear(distance, angle)
				print(xy)
				csv_writer.writerow(xy)
			
			
		