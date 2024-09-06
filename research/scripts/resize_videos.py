import os
import csv
import argparse
from moviepy.editor import VideoFileClip
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

# Set the directory containing your .mp4 files
directory = './processed_videos/clipped_videos'
output_directory = './processed_videos/clipped_resized_videos'  # Where to save the processed files

# Make sure the output directory exists
os.makedirs(output_directory, exist_ok=True)

def process_video(input_path, output_path, resolution=324):
    """Reduce video resolution to the specified resolution and remove audio."""
    try:
        # Skip processing if the output file already exists
        # if os.path.exists(output_path):
        # print(f"Skipped {output_path}, already exists.")
        # return

        with VideoFileClip(input_path) as video:
            width, height = video.size
            
            if height > resolution:
                # Calculate the new width to maintain aspect ratio
                new_width = int((resolution / height) * width)
                
                # Resize video
                video_resized = video.resize(newsize=(new_width, resolution))
                # print(f"Resized {input_path} from {width}x{height} to {new_width}x{resolution}")
            else:
                video_resized = video
                # print(f"Video {input_path} is already {width}x{height} or lower, no resizing needed.")

            # Remove audio
            video_resized = video_resized.without_audio()
            
            # Write the result to the output directory
            video_resized.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                logger=None,
                ffmpeg_params=[
                    '-profile:v', 'main',  # For Safari compatibility
                    '-pix_fmt', 'yuv420p'  # For Firefox compatibility
                ]
            )
            print(f"Processed {input_path} to {output_path}")

    except Exception as e:
        print(f"Failed to process {input_path}: {e}")

def get_files_to_process(directory, csv_file=None):
    """Get the list of files to process based on an optional CSV file."""
    video_files = [f for f in os.listdir(directory) if f.endswith('.mp4')]

    if csv_file:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            narration_ids = {row['narration_id'] for row in reader}
        # Filter the video files based on the narration_id from the CSV
        video_files = [f for f in video_files if os.path.splitext(f)[0] in narration_ids]

    return video_files

def main():
    parser = argparse.ArgumentParser(description="Process videos by reducing resolution and removing audio.")
    parser.add_argument('--csv_file', type=str, help="Optional CSV file to filter video files by narration_id.")
    args = parser.parse_args()

    video_files = get_files_to_process(directory, args.csv_file)
    print(f"Processing {len(video_files)} videos")




    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(process_video, os.path.join(directory, filename), os.path.join(output_directory, filename)): filename
            for filename in video_files
        }

        
        with tqdm(total=len(futures), desc="Processing videos") as pbar:
            # let's give it some more threads:
            # with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # for future in concurrent.futures.as_completed(futures):
            #         arg = futures[future]
            #         results[arg] = future.result()
            #         pbar.update(1)

            # Use tqdm to track progress
            for future in as_completed(futures):
                try:
                    future.result(timeout=1*60)
                except Exception as e:
                    print(f"Error processing video: {e}")
                
                pbar.update(1)

    print("Processing complete.")

if __name__ == "__main__":
    main()
