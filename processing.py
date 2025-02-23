import pandas as pd
import numpy as np
from numpy import sin, cos
import csv
import numpy as np
import argparse

print("What file do you want to process?")
points = input()

file_name = points.rsplit('points_')[1]
file_name = file_name.rsplit('.csv')[0]

file_path = '/Users/mickelpickle/Documents/GitHub/MRL-Project/CSVFiles/processed_data' 
file_name = f"{file_path}/points3d_{file_name}.txt"

# Clean up any rows of the csv that do not work
fn_in = points
fn_out = 'outfile.csv'

with open(fn_in, 'r', errors='ignore') as inp, open(fn_out, 'w') as out:
    writer = csv.writer(out)
    for row in csv.reader(inp):
        try: 
            if len(row)==6:
                writer.writerow(row)
        except Exception as e:
            continue

# Convert the distance and theta points of the lidar into cartesian coordinates
def polCart(theta, distance):
   if isinstance(theta, str):
       return 0, 0
   theta = (2 * np.pi) - np.radians(theta + 180)
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
    R_z = data['R_z']
    
    with open(file_name, mode='w') as csvfile:
        for i in range(len(angle)):
            try:
                rectCoords = polCart(angle[i], distance[i])
                rectCoords = rotateX(rectCoords[0], rectCoords[1], rectCoords[2], R_x[i])
                rectCoords = rotateY(rectCoords[0], rectCoords[1], rectCoords[2], R_y[i])

                coord_line = f"{rectCoords[0]} {rectCoords[1]} {rectCoords[2]}\n"
                csvfile.write(coord_line)
            except Exception:
                continue
            
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
    
    # Create new filename with voxel size
    base_name = csv_file.rsplit('.', 1)[0]  # Remove extension
    base_name = base_name.rsplit('points3d_')[1]
    
    new_file = f"/Users/mickelpickle/Documents/GitHub/MRL-Project/CSVFiles/voxelized_data/voxel3d_{base_name}.txt"
    
    # Save to new file instead of overwriting
    pd.DataFrame(voxel_centers, columns=["x", "y", "z"]).to_csv(new_file, index=False, header=False, sep=' ')
    
    return len(unique_voxels), new_file

def main():
    
    parser = argparse.ArgumentParser(description='Voxelize the point cloud from a CSV file')
    parser.add_argument('csv_file', type=str, help='Path to the input CSV file')
    parser.add_argument('--voxel-size', type=float, default=0.1, help='Size of each voxel (default: 0.1)')
    
    args = parser.parse_args()
    
    try:
        num_voxels, output_file = voxelize_point_cloud(args.csv_file, args.voxel_size)
        print(f"Voxelized point cloud contains {num_voxels} unique voxels.")
        print(f"Results saved to: {output_file}")
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.csv_file}'")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()  