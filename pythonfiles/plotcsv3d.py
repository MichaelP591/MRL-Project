from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np
from numpy import sin, cos
import csv
import numpy as np
from scipy.spatial import cKDTree

# Take the raw lidar and servo data and convert it into 3d points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

def remove_redundant_points(points, tolerance=1e-3, voxel_size=0.1):
    """
    Removes near-duplicate 3D points and performs downsampling.
    
    Args:
        points (np.ndarray): Nx3 array of 3D points.
        tolerance (float): Minimum distance between distinct points.
        voxel_size (float): Size of voxels for downsampling.

    Returns:
        np.ndarray: Filtered set of 3D points.
    """
    # Round points to the nearest voxel to downsample
    voxel_grid = np.round(points / voxel_size) * voxel_size
    unique_voxel_keys, unique_indices = np.unique(voxel_grid, axis=0, return_index=True)
    
    # Get unique points after voxel downsampling
    filtered_points = points[unique_indices]

    # Further refine by removing near-duplicates using a KD-Tree
    tree = cKDTree(filtered_points)
    keep_indices = []
    visited = set()

    for i, point in enumerate(filtered_points):
        if i in visited:
            continue
        neighbors = tree.query_ball_point(point, tolerance)
        keep_indices.append(i)
        visited.update(neighbors)

    return filtered_points[keep_indices]

#All necessary functions
def polCart(theta, distance):
    if isinstance(theta, str):
        return 0, 0
    # Convert the distance and theta points of the lidar into cartesian coordinates
    theta = (2 * np.pi) - np.radians(theta)
    x = float(distance) * cos(theta)
    y = float(distance) * sin(theta)
    return x, y, 0

def rotateX(x, y, z, R_x):
    R_x = np.radians(float(R_x))
    # Rotate the lidar about the x axis
    distanceangle = np.array([x, y, z])

    transformx = np.array([
        [1, 0, 0],
        [0, cos(R_x), -sin(R_x)], 
        [0, sin(R_x), cos(R_x)]
        ])
    
    transformed = np.dot(transformx, distanceangle)
    return round(transformed[0], 3), round(transformed[1], 3), round(transformed[2], 3)

def rotateY(x, y, z, R_y):
    R_y = np.radians(float(R_y))
    # Rotate the lidar about the y axis
    distanceangle = np.array([x, y, z])

    transformy = np.array([
        [cos(R_y), 0, sin(R_y)],
        [0, 1, 0], 
        [-sin(R_y), 0, cos(R_y)]
        ])
    
    transformed = np.dot(transformy, distanceangle)
    return round(transformed[0], 3), round(transformed[1], 3), round(transformed[2], 3)

def rotateY(x, y, z, R_z):
    R_z = np.radians(float(R_z))
    # Rotate the lidar about the z axis
    distanceangle = np.array([x, y, z])

    transformy = np.array([
        [cos(R_z), -sin(R_z), 0],
        [sin(R_z), cos(R_z), 0], 
        [0, 0, 1]
        ])
    
    transformed = np.dot(transformy, distanceangle)
    return round(transformed[0], 3), round(transformed[1], 3), round(transformed[2], 3)

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
    ax.scatter(x, y, z, s=10)

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
                coordsArray = np.array
            except Exception:
                continue
    
    df = pd.read_csv("points3d.csv")
    points = df[['x', 'y', 'z']].values
    filtered_points = remove_redundant_points(points)

    df_filtered = pd.DataFrame(filtered_points, columns=['X', 'Y', 'Z'])
    df_filtered.to_csv('points3d.csv', index=False)

ani = FuncAnimation(plt.gcf(), animate, interval=50, cache_frame_data=False)

plt.tight_layout()
plt.show()