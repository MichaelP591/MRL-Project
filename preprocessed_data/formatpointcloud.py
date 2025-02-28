import os
import shutil
import sys
from pathlib import Path
import subprocess
import stat

def ensure_directory_permissions(path):
    """Ensure the directory has the correct permissions"""
    try:
        if not os.path.exists(path):
            os.makedirs(path, mode=0o755, exist_ok=True)
        else:
            os.chmod(path, 0o755)  # rwxr-xr-x permissions
        return True
    except PermissionError as e:
        print(f"Permission error for directory {path}: {e}")
        print("Try running the script with sudo or check directory permissions")
        return False

def create_pointcloud_structure(input_txt_file):
    print("Starting pointcloud formatting process...")
    
    # Verify input file exists
    if not os.path.exists(input_txt_file):
        print(f"Error: Input file {input_txt_file} not found!")
        sys.exit(1)
    
    # Get the base directory (where Stanford3dDataset is located)
    current_dir = Path(__file__).parent.parent
    s3dis_path = current_dir / "data" / "s3dis" / "Stanford3dDataset_v1.2_Aligned_Version" / "Area_1"
    
    print(f"Working directory: {s3dis_path}")
    
    # Check directory permissions
    if not ensure_directory_permissions(s3dis_path):
        sys.exit(1)
    
    # Prompt for pointcloud name
    pointcloud_name = input("Please enter the name for your pointcloud: ")
    
    # Create the new directory structure
    new_folder = s3dis_path / f"{pointcloud_name}_1"
    annotations_folder = new_folder / "Annotations"
    
    print(f"Creating directory structure for {pointcloud_name}_1...")
    
    # Create directories with proper permissions
    try:
        os.makedirs(annotations_folder, mode=0o755, exist_ok=True)
    except PermissionError as e:
        print(f"Permission error creating directories: {e}")
        print("Try running the script with sudo or check directory permissions")
        sys.exit(1)
    
    # Copy files
    print("Copying and creating required files...")
    
    try:
        # Copy to Annotations/wall_1.txt
        wall_txt_path = annotations_folder / "wall_1.txt"
        shutil.copy2(input_txt_file, wall_txt_path)
        os.chmod(wall_txt_path, 0o644)  # rw-r--r-- permissions
        print(f"Created {wall_txt_path}")
        
        # Copy to [pointcloud_name]_1.txt
        main_txt_path = new_folder / f"{pointcloud_name}_1.txt"
        shutil.copy2(input_txt_file, main_txt_path)
        os.chmod(main_txt_path, 0o644)  # rw-r--r-- permissions
        print(f"Created {main_txt_path}")
        
        # Create empty Icon file
        icon_path = new_folder / "Icon"
        icon_path.touch(mode=0o644)
        print(f"Created empty Icon file at {icon_path}")
        
    except PermissionError as e:
        print(f"Permission error while copying files: {e}")
        print("Try running the script with sudo or check file permissions")
        sys.exit(1)
    
    print("\nPointcloud formatting completed successfully!")
    
    # Add path to anno_paths.txt
    print("Updating anno_paths.txt...")
    anno_paths_file = current_dir / "data_utils" / "meta" / "anno_paths.txt"
    
    try:
        # Read existing content
        existing_content = []
        if os.path.exists(anno_paths_file):
            with open(anno_paths_file, 'r') as f:
                existing_content = f.readlines()
        
        # Prepare new path
        new_path = f"Area_1/{pointcloud_name}_1/Annotations\n"
        
        # Add new path at the beginning
        updated_content = [new_path] + existing_content
        
        # Write back to file
        with open(anno_paths_file, 'w') as f:
            f.writelines(updated_content)
        os.chmod(anno_paths_file, 0o644)  # rw-r--r-- permissions
        
        print(f"Added '{new_path.strip()}' to anno_paths.txt")
        
    except PermissionError as e:
        print(f"Permission error while updating anno_paths.txt: {e}")
        print("Try running the script with sudo or check file permissions")
        sys.exit(1)
    
    # Run collect_indoor3d_data.py
    print("\nRunning collect_indoor3d_data.py...")
    collect_script_path = current_dir / "data_utils" / "collect_indoor3d_data.py"
    
    try:
        subprocess.run([sys.executable, str(collect_script_path)], check=True)
        print("Successfully completed collect_indoor3d_data.py")
    except subprocess.CalledProcessError as e:
        print(f"Error running collect_indoor3d_data.py: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"Permission error running collect_indoor3d_data.py: {e}")
        print("Try running the script with sudo or check script permissions")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python formatpointcloud.py <input_txt_file>")
        sys.exit(1)
    
    create_pointcloud_structure(sys.argv[1])
