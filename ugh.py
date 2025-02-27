
import pandas as pd
import os
import csv
import numpy as np

print("Enter a folder to process: ")
folder_path = input()

for file in os.listdir(folder_path):
    try: 
        file_path = os.path.join(folder_path, file)
        
        if os.path.isfile(file_path):
            print(f"Reading: {file}")
            
            points = file_path
            new_file = points.replace('.txt', '_processed.txt')
            
            # First read the header to get column names
            with open(points, 'r') as f:
                first_line = f.readline().strip()
                columns = first_line.split(' ')
            
            # Read the file with the detected columns
            df = pd.read_csv(points, 
                           sep=' ',
                           names=columns,  # Use detected column names
                           skiprows=1)     # Skip header row
            
            # Select specific columns regardless of their position
            required_columns = ['X', 'Y', 'Z', 'R', 'G', 'B', 'Nx', 'Ny', 'Nz']
            df_selected = df[required_columns]
            
            # Write to new file
            df_selected.to_csv(new_file, 
                             index=False, 
                             header=False,  # Keep headers in output
                             sep=' ')
            
            print(f"Processed file saved as: {new_file}")
            
    except KeyError as ke:
        print(f"Missing required column in {file}: {ke}")
    except Exception as ex:
        print(f"Error processing {file}: {ex}")
        continue