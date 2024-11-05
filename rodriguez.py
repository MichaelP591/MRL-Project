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
    phi = np.radians(phi-90)
    x = distance * np.cos(theta)
    y = distance * np.sin(theta)
    distanceangle = np.array([x, y, 0, 1])
    transformx = np.array([
        [1, 0, 0, 0], 
        [0, np.cos(phi), -1*np.sin(phi), 0], 
        [0, np.sin(phi), np.cos(phi), 0], 
        [0, 0, 0, 1]
        ])
    transformed = np.matmul(distanceangle, transformx)
    x = transformed[0]
    y = transformed[1]
    z = transformed[2]
    return x, y, z

distance = 1
theta = 90
x_array = []
y_array = []
z_array = []

for i in range(91, 10):
    pol2cart(distance, theta, i)
    x = pol2cart[0]  
    y = pol2cart[1]
    z = pol2cart[2]
    x_array.append[x]
    y_array.append[y]
    z_array.append[z]
    
ax.scatter(x_array,y_array,z_array,s=1)

plt.tight_layout()
plt.show()