from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np
import csv
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

def pol2cart(distance, theta, phi):
    theta = (2 * np.pi) - theta 
    phi = np.radians(phi)
    x = distance * np.cos(theta) * np.sin(phi) 
    y = distance * np.sin(theta) * np.sin(phi)
    z = distance * np.cos(phi) 
    return x, y, z
    

with open('points.csv', mode='r') as csvfile:
    data = pd.read_csv('points.csv', index_col=0)
    data = pd.read_csv('points.csv')

    angle = data['angle']    
    distance = data['distance']
    zangle = data['servo']
    with open('points3d.csv', mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',') 
        csv_writer.writerow(['x', 'y', 'z'])
        for i in range(len(angle)):
            cart = pol2cart(distance[i], angle[i], zangle[i])           
            csv_writer.writerow([cart[0], cart[1], cart[2]])


with open('points3d.csv', mode='r') as csvfile:
    data = pd.read_csv('points3d.csv', index_col=0)

def animate(i):
    data = pd.read_csv('points3d.csv')
    x = data['x']    
    y = data['y']
    z = data['z']
    plt.cla()
    ax.scatter(x, y, z, s=1)


ani = FuncAnimation(plt.gcf(), animate, interval=5, cache_frame_data=False)

print(data)

plt.tight_layout()
plt.show()