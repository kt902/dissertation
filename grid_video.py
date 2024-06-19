# This scripts generates a grid of video segmenets with each grid containing both the video and a text label of the action taking place.
# 
# This is done using: 
# 1. mp4 files in the current directory (and its subdirectories)
# 2. A epic_sample.csv file in the current directory
# 
import glob
import random
from statistics import mean
from moviepy.editor import VideoFileClip, clips_array, TextClip, ColorClip, CompositeVideoClip
import os
import pandas as pd
from PIL import Image as pil
from pkg_resources import parse_version

if parse_version(pil.__version__)>=parse_version('10.0.0'):
    Image.ANTIALIAS=Image.LANCZOS

# Load the CSV file
df = pd.read_csv('./epic_sample.csv')

# Step 1: Find all mp4 files in the current directory
video_files = glob.glob('**/*.mp4', recursive=True)

grid_size = 4

# Extract identifiers from filenames
# Example assumes filenames include relevant ids as the last part before '.mp4', e.g., '.../P01_01_100.mp4'
file_ids = [os.path.splitext(os.path.basename(file))[0] for file in video_files]

# Extract unique narration_ids from DataFrame for comparison
# Adjust the column name or manipulation as necessary to match file_ids
narration_ids = set(df['narration_id'].apply(lambda x: str(x)))  # Convert to set for faster lookup

# Filter video files based on whether the extracted id from each file is in narration_ids
filtered_files = [file for file, file_id in zip(video_files, file_ids) if file_id in narration_ids]

# Step 2: Randomly select 25 videos
if len(video_files) >= grid_size*grid_size:
    selected_files = random.sample(filtered_files, grid_size*grid_size)
else:
    raise ValueError(f"Not enough video files in the directory to create a {grid_size}x{grid_size} grid.")

# Load the selected video files
videos = [VideoFileClip(file).resize(height=1000 // grid_size) for file in selected_files]  # Resize to uniform size, adjust as needed

# Set duration to the shortest video in the grid to avoid errors
min_duration = mean(video.duration for video in videos)
# videos = [video.subclip(0, min_duration) for video in videos]

file_ids = [os.path.splitext(os.path.basename(file))[0] for file in selected_files]

for index, video in enumerate(videos):
    video_id = file_ids[index]
    narration = df[df['narration_id'] == video_id]['narration'].item()

    # Create a text clip (customize with your text and options)
    # Set the fontsize of the text, the color, and the font (if it's available)
    text = TextClip(f"{video_id}: {narration}", fontsize=18, color='white', font="Arial-bold")

    # Create a background rectangle
    bg_color = ColorClip(size=(text.size[0]+10, text.size[1]+10), color=(0,0,0)).set_opacity(0.5)

    # Set duration and position for the background equal to text
    bg_color = bg_color.set_duration(video.duration).set_position(('center', 'bottom'))

    # Set duration and position for the text
    text = text.set_duration(video.duration).set_position(('center', 'bottom'))

    # Composite text on background
    text_on_bg = CompositeVideoClip([bg_color, text])
    # Set the duration of the text clip
    # text = text.set_duration(video.duration)  # Duration in seconds

    # Set the position of the text in the video. Options include 'center', coordinates like (x,y), or functions.
    text_on_bg = text_on_bg.set_position(('center', 'bottom'))
    videos[index] = CompositeVideoClip([video, text_on_bg])

# Organize the clips into a {grid_size}x{grid_size} grid
grid = clips_array([videos[i*grid_size:(i+1)*grid_size] for i in range(grid_size)])

# Write the result to a file
grid.write_videofile("video_grid.mp4", codec='libx264')
