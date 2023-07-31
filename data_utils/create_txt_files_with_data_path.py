import os
import glob

def create_dataset_files(source_dir, target_dir):
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)

    # Get the list of subdirectories in the source directory
    subdirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]

    # For each subdirectory
    for subdir in subdirs:
        subdir_path = os.path.join(source_dir, subdir)

        # Get the list of npy files in the subdirectory
        npy_files = glob.glob(os.path.join(subdir_path, "*.npy"))

        # Create a txt file in the target directory
        with open(os.path.join(target_dir, f"{subdir}.txt"), "w") as f:
            # For each npy file, write its path in the txt file
            for npy_file in npy_files:
                f.write(f"{npy_file}\n")

# Usage
source_dir = "/home/alexandrtchk/VSCode/multimodal/data-1000-items/splitted"
target_dir = "/home/alexandrtchk/VSCode/multimodal/data-1000-items/splitted/dataset_files_paths"

create_dataset_files(source_dir, target_dir)
