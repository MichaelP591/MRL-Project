from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np
import csv

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

with open('points3d.csv', mode='r') as csvfile:
    data = pd.read_csv('points3d.csv', index_col=0)

def animate(i):
    data = pd.read_csv('points3d.csv')
    x = data['x']    
    y = data['y']
    z = data['z']
    plt.cla()
    ax.scatter(0,0,0, s=50, color='r')
    ax.set_xlabel(r'$x$', fontsize='large')
    ax.set_ylabel(r'$y$', fontsize='large')
    ax.set_zlabel(r'$z$', fontsize='large')
    ax.scatter(x, y, z, s=1)

ani = FuncAnimation(plt.gcf(), animate, interval=50, cache_frame_data=False, )

plt.tight_layout()
plt.show()