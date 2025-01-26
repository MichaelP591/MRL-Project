from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import csv

# Take the raw lidar and servo data and convert it into 3d points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plt.cla()
ax.scatter(0,0,0, s=50, color='r')
ax.set_xlabel(r'$x$', fontsize='large')
ax.set_ylabel(r'$y$', fontsize='large')
ax.set_zlabel(r'$z$', fontsize='large')

# Function to convert polar coordinates to cartesian coordinates
def pol2cart(distance, theta, phi):
    # Convert all inputs to float
    distance = float(distance)
    theta = float(theta)
    phi = float(phi)
    
    # Convert angles to radians
    theta = (2 * np.pi) - np.radians(theta)
    phi = np.radians(float(phi)-135)
    
    # Calculate initial coordinates
    x = distance * np.cos(theta)
    y = distance * np.sin(theta)
    distanceangle = np.array([x, y, 0])
    
    # Create transformation matrix
    transformx = np.array([
        [1, 0, 0],
        [0, np.cos(phi), np.sin(phi)], 
        [0, -1*np.sin(phi), np.cos(phi)]
    ])
    
    # Apply transformation
    transformed = np.matmul(transformx, distanceangle)
    return transformed[0], transformed[1], transformed[2]

with open('outfile.csv', mode='r') as csvfile:
    data = pd.read_csv('outfile.csv', dtype={'timestamp': int, 'angle': float, 'distance': int, 'servo': int}, low_memory=False)

    with open('points3d.csv', mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',') 
        csv_writer.writerow(['x', 'y', 'z'])

        for i in range(len(data)):
            try: 
                cart = pol2cart(data['distance'][i], data['angle'][i], data['servo'][i])          
                csv_writer.writerow([cart[0], cart[1], cart[2]])
            except (ValueError, TypeError) as e:
                continue
