import os
import tarfile
import glob
from tqdm.auto import tqdm

directories = [
    f"/home/ec2-user/environment/torrents/epic-torrents-1/2g1n6qdydwa9u22shpxqzp0t8m/",
    f"/home/ec2-user/environment/torrents/epic-torrents/3h91syskeag572hl6tvuovwv4d/frames_rgb_flow/rgb/",
]

# Initialize an empty list to hold all found .tar files
tar_files = []

# Loop through each directory and find all .tar files
for base_dir in directories:
    tar_files.extend(glob.glob(os.path.join(base_dir, "**/*.tar"), recursive=True))

for tar_file in tqdm(tar_files):
    if "flow_frames" in tar_file:
        continue

    print(tar_file)

    # Determine the directory name by stripping the .tar extension
    target_dir = tar_file.rsplit('.', 1)[0]
    
    # Check if the directory already exists
    if not os.path.exists(target_dir):
        print(f"Extracting {tar_file} to {target_dir}")

        # Extract the tar file
        with tarfile.open(tar_file, "r") as tar:
            tar.extractall(path=target_dir)
    else:
        print(f"Skipping {tar_file} because {target_dir} already exists.")
    # break
