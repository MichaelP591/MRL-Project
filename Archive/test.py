import open3d as o3d
import numpy as np
import os
import sys
import pandas as pd

# Load CSV file
csv_file = "points3d.csv"  # Replace with your CSV filename
df = pd.read_csv(csv_file)

# Ensure the CSV has the required columns
if df.shape[1] < 3:
    raise ValueError("CSV file must have at least three columns for x, y, and z coordinates.")

# Convert DataFrame to NumPy array (only the first 3 columns)
points = df.iloc[:, :3].to_numpy()
print(points)

# Create Open3D PointCloud object
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
o3d.io.write_point_cloud("sync.ply", pcd)

# Visualize the point cloud
pcd_load = o3d.io.read_point_cloud("sync.ply")
o3d.visualization.draw_geometries([pcd_load])

