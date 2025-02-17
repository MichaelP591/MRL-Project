import pandas as pd
import numpy as np
from numpy import sin, cos
import csv
import numpy as np

# Clean up any rows of the csv that do not work
fn_in = 'points.csv'
fn_out = 'outfile.csv'

with open(fn_in, 'r') as inp, open(fn_out, 'w') as out:
   writer = csv.writer(out)
   for row in csv.reader(inp):
       if len(row)==6:
           writer.writerow(row)

# Convert the distance and theta points of the lidar into cartesian coordinates
def polCart(theta, distance):
   if isinstance(theta, str):
       return 0, 0
   theta = (2 * np.pi) - np.radians(theta)
   x = float(distance) * cos(theta)
   y = float(distance) * sin(theta)
   return x, y, 0

# Rotate the lidar about the x axis
def rotateX(x, y, z, R_x):
   R_x = np.radians(float(R_x))
   distanceangle = np.array([x, y, z])
   transformx = np.array([
       [1, 0, 0],
       [0, cos(R_x), -sin(R_x)],
       [0, sin(R_x), cos(R_x)]
       ])
  
   transformed = np.dot(transformx, distanceangle)
   return round(transformed[0], 3), round(transformed[1], 3), round(transformed[2], 3)


# Rotate the lidar about the y axis
def rotateY(x, y, z, R_y):
   R_y = np.radians(float(R_y))
   distanceangle = np.array([x, y, z])
   transformy = np.array([
       [cos(R_y), 0, sin(R_y)],
       [0, 1, 0],
       [-sin(R_y), 0, cos(R_y)]
       ])
   transformed = np.dot(transformy, distanceangle)
   return round(transformed[0], 3), round(transformed[1], 3), round(transformed[2], 3)


# Rotate the lidar about the z axis
def rotateZ(x, y, z, R_z):
   R_z = np.radians(float(R_z))
   distanceangle = np.array([x, y, z])
   transformy = np.array([
       [cos(R_z), -sin(R_z), 0],
       [sin(R_z), cos(R_z), 0],
       [0, 0, 1]
       ])
   transformed = np.dot(transformy, distanceangle)
   return round(transformed[0], 3), round(transformed[1], 3), round(transformed[2], 3)

#main
with open('outfile.csv', mode='r') as csvfile:
   data = pd.read_csv('outfile.csv', index_col=0)
   data = pd.read_csv('outfile.csv')

   angle = data['angle']  
   distance = data['distance']
   R_x = data['R_x']
   R_y = data['R_y']

   with open('points3d.csv', mode='w', newline='') as csvfile:
       csv_writer = csv.writer(csvfile, delimiter=',')
       csv_writer.writerow(['x', 'y', 'z'])

       for i in range(len(angle)):
           try:
               rectCoords = polCart(angle[i], distance[i])
               rectCoords = rotateX(rectCoords[0], rectCoords[1], rectCoords[2], R_x[i])
               rectCoords = rotateY(rectCoords[0], rectCoords[1], rectCoords[2], R_y[i])
               csv_writer.writerow(rectCoords)
           except Exception:
               continue