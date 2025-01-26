from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np
import csv

# Take the raw lidar and servo data and convert it into 3d points

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

def pol2cart(distance, theta, phi):
    distance = float(distance)
    theta = float(theta)
    phi = float(phi)
    theta = (2 * np.pi) - float(np.radians(theta)) 
    phi = np.radians(float(phi-135))
    x = float(distance) * np.cos(theta)
    y = float(distance) * np.sin(theta)
    distanceangle = np.array([x, y, 0])
    transformx = np.array([
        [1, 0, 0],
        [0, np.cos(phi), np.sin(phi)], 
        [0, -1*np.sin(phi), np.cos(phi)]
        ])
    transformed = np.matmul(transformx, distanceangle)
    x = transformed[0]
    y = transformed[1]
    z = transformed[2]
    return x, y, z

with open('outfile.csv', mode='r') as csvfile:
    data = pd.read_csv('outfile.csv', index_col=0)
    data = pd.read_csv('outfile.csv')

    angle = data['angle']    
    distance = data['distance']
    zangle = []
    for servo in data['servo'][1:]:  # Skip header row
        try:
            servo_val = int(servo)
            zangle.append((4.286/3) * (servo_val - 33))
        except ValueError:
            continue

    for servo in zangle:
        servo = (4.286/3) * (servo - 33)
    with open('points3d.csv', mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',') 
        csv_writer.writerow(['x', 'y', 'z'])
        for i in range(len(angle)):
            cart = pol2cart(distance[i], angle[i], zangle[i])           
            csv_writer.writerow([cart[0], cart[1], cart[2]])

def animate(i):
    data = pd.read_csv('points3d.csv', on_bad_lines='skip')
    x = data['x']    
    y = data['y']
    z = data['z']
    plt.cla()
    ax.scatter(0,0,0, s=50, color='r')
    ax.set_xlabel(r'$x$', fontsize='large')
    ax.set_ylabel(r'$y$', fontsize='large')
    ax.set_zlabel(r'$z$', fontsize='large')
    ax.scatter(x, y, z, s=1)

ani = FuncAnimation(plt.gcf(), animate, interval=50, cache_frame_data=False)

plt.tight_layout()
plt.show()