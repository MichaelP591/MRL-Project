import pandas as pd
import numpy as np
import argparse

def voxelize_point_cloud(csv_file, voxel_size):
    #idk exactly how points are stored in the csv file
    df = pd.read_csv(csv_file, names=["x", "y", "z"])
    
    voxel_indices = np.floor(df / voxel_size).astype(int)
    
    # use a set to store unique voxel indices
    unique_voxels = set(map(tuple, voxel_indices.values))
    
    return unique_voxels

def main():
    # this is a command line interface for the  function
    parser = argparse.ArgumentParser(description='voxelize the point cloud from CSV file')
    parser.add_argument('csv_file', type=str, help='Path to the input CSV file')
    parser.add_argument('--voxel-size', type=float, default=0.1,
                        help='Size of each voxel (default: 0.1)')
    
    args = parser.parse_args()
    
    try:
        voxels = voxelize_point_cloud(args.csv_file, args.voxel_size)
        print(f"Voxelized point cloud contains {len(voxels)} unique voxels.")
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.csv_file}'")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()

# sample run: python voxel.py input.csv --voxel-size 0.1 
# basically this is a python file and you can run it with a command line arg and it will vowelize the pointcloud