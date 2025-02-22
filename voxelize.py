import pandas as pd
import numpy as np
import argparse

def voxelize_point_cloud(csv_file, voxel_size):
    # Read point cloud data from CSV
    #this might work
    df = pd.read_csv(csv_file, header=0)  # Read CSV
    df = df.apply(pd.to_numeric, errors='coerce')  # Convert all to numbers, force non-numbers to NaN
    df = df.dropna()  # Remove any rows with NaN values
    
    voxel_indices = np.floor(df / voxel_size).astype(int)
    
    # remove duplicate voxel index
    unique_voxels = np.array(list(set(map(tuple, voxel_indices.values))))
    
    # convert back to coordinates
    voxel_centers = (unique_voxels + 0.5) * voxel_size
    
    # overwrite the CSV  
    pd.DataFrame(voxel_centers, columns=["x", "y", "z"]).to_csv(csv_file, index=False, header=False)
    
    return len(unique_voxels)

def main():
    parser = argparse.ArgumentParser(description='Voxelize the point cloud from a CSV file')
    parser.add_argument('csv_file', type=str, help='Path to the input CSV file')
    parser.add_argument('--voxel-size', type=float, default=0.1, help='Size of each voxel (default: 0.1)')
    
    args = parser.parse_args()
    
    try:
        num_voxels = voxelize_point_cloud(args.csv_file, args.voxel_size)
        print(f"Voxelized point cloud contains {num_voxels} unique voxels. The file has been updated.")
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.csv_file}'")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()

# sample run: python voxelize.py input.csv --voxel-size 0.1 
# basically this is a python file and you can run it with a command line arg and it will vowelize the pointcloud
