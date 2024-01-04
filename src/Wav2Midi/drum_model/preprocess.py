import os
import shutil

# Define the drum types
DRUM_TYPES = ['hat', 'tom', 'ride', 'open', 'kick', 'bongo', 'clap', 'snare', 'rim', 'snap', 'crash', 'shaker']

# Define the source directory
source_dir = 'MDB_subset/drums'

# Define the target directory
target_dir = 'MDB_subset/kit'

# Create the target directories if they don't exist
for drum_type in DRUM_TYPES:
    os.makedirs(os.path.join(target_dir, drum_type), exist_ok=True)

# Walk through the source directory
for root, dirs, files in os.walk(source_dir):
    for file in files:
        # Check if the file matches one of the drum types
        for drum_type in DRUM_TYPES:
            if drum_type in file.lower():
                # Copy the file to the corresponding target directory
                shutil.copy(os.path.join(root, file), os.path.join(target_dir, drum_type))