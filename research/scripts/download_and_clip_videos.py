import os
import pandas as pd
import requests
from tqdm import tqdm
from moviepy.video.io.VideoFileClip import VideoFileClip
import argparse
import boto3
import io
import concurrent.futures
import multiprocessing

class EpicURLBuilder:
    def __init__(self,
                 epic_55_base_url='https://data.bris.ac.uk/datasets/3h91syskeag572hl6tvuovwv4d',
                 epic_100_base_url='https://data.bris.ac.uk/datasets/2g1n6qdydwa9u22shpxqzp0t8m',
                 epic_55_splits=None):
        self.base_url_55 = epic_55_base_url.rstrip('/')
        self.base_url_100 = epic_100_base_url.rstrip('/')
        self.splits = self.load_splits(epic_55_splits) if epic_55_splits else {}

    def load_splits(self, splits_source):
        if splits_source.startswith('http://') or splits_source.startswith('https://'):
            response = requests.get(splits_source)
            splits_df = pd.read_csv(io.StringIO(response.text))
        else:
            splits_df = pd.read_csv(splits_source)

        splits_dict = {}
        for _, row in splits_df.iterrows():
            splits_dict[row['video_id']] = row['split']
        return splits_dict

    def get_video_url(self, video_id, file_ext='MP4'):
        parts = video_id.split('_')
        participant = parts[0]
        is_extension = len(parts[1]) == 3  # Detect if it's an EPIC 100 extension video (e.g., P01_001)

        if is_extension:
            # EPIC 100 video
            url = f"{self.base_url_100}/{participant}/videos/{video_id}.{file_ext}"
        else:
            # EPIC 55 video
            split = self.splits.get(video_id, 'train')  # Default to 'train' if split is not found
            url = f"{self.base_url_55}/videos/{split}/{participant}/{video_id}.{file_ext}"

        return url

# Function to download video
def download_video(video_id, output_path, url_builder):
    video_url = url_builder.get_video_url(video_id)
    
    response = requests.get(video_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kilobyte

    with open(output_path, 'wb') as file, tqdm(
            desc=f'Downloading {video_id}',
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(block_size):
            bar.update(len(data))
            file.write(data)

# Function to clip videos from a single loaded video
# Function to clip videos from a single loaded video
def clip_videos(video, group, output_folder, bucket_name, lock, tracking_file):
    for _, task in group.iterrows():
    # for _, task in tqdm(group.iterrows(), total=len(group), desc="Processing clips", unit="clip"):
        narration_id = task['narration_id']
        start_time = task['start_timestamp']
        end_time = task['stop_timestamp']

        output_clip_path = os.path.join(output_folder, f'{narration_id}.mp4')
        s3_key_clip = f'EK-100/{narration_id}.mp4'

        # Clip the video
        new_clip = video.subclip(start_time, end_time)
        new_clip.write_videofile(output_clip_path, codec='libx264', logger=None)

        # Upload the clipped video to S3
        # upload_to_s3(output_clip_path, bucket_name, s3_key_clip)

        # Delete the clipped file after upload
        # if os.path.exists(output_clip_path):
        #     os.remove(output_clip_path)
        #     print(f"Deleted {output_clip_path} after upload.")

        # Update tracking file safely after processing each clip
        with lock:
            df = pd.DataFrame([task])
            if os.path.exists(tracking_file):
                tracking_df = pd.read_csv(tracking_file)
            else:
                tracking_df = pd.DataFrame(columns=df.columns)

            tracking_df = pd.concat([tracking_df, df], ignore_index=True)
            tracking_df.to_csv(tracking_file, index=False)

# Function to upload to S3 with sync and progress bar
def upload_to_s3(file_path, bucket_name, s3_key):
    s3_client = boto3.client('s3')
    file_size = os.path.getsize(file_path)
    # Check if the file exists in S3 and if it matches the local file
    try:
        s3_obj = s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        s3_etag = s3_obj['ETag'].strip('"')
        local_md5 = calculate_md5(file_path)

        if '-' not in s3_etag and s3_etag == local_md5:
            print(f"File {s3_key} already exists in S3 with matching content, skipping upload.")
            return
        else:
            # Fallback to comparing file sizes if the MD5 comparison is inconclusive
            s3_size = s3_obj['ContentLength']
            if s3_size == file_size:
                print(f"File {s3_key} already exists in S3 with matching size, skipping upload.")
                return

    except s3_client.exceptions.ClientError:
        pass  # The file doesn't exist in S3, so we'll upload it

    
    with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, desc=f'Uploading {s3_key}') as bar:
        s3_client.upload_file(
            Filename=file_path, 
            Bucket=bucket_name, 
            Key=s3_key,
            Callback=lambda bytes_transferred: bar.update(bytes_transferred)
        )
    print(f"Uploaded {file_path} to s3://{bucket_name}/{s3_key}")

# Function to calculate the MD5 checksum of a file
def calculate_md5(file_path):
    import hashlib
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Function to process a group of rows for the same video
def process_video_group(video_id, group, output_folder, bucket_name, strategy, url_builder, lock, tracking_file):
    if strategy == 'download':
        video_path = os.path.join(output_folder, f'{video_id}.mp4')
        if not os.path.exists(video_path):
            download_video(video_id, video_path, url_builder)
    elif strategy == 'local':
        video_path = url_builder.get_video_url(video_id)

    # Load the video once
    with VideoFileClip(video_path) as video:
        clip_videos(video, group, output_folder, bucket_name, lock, tracking_file)

    # Upload the entire video file to S3
    s3_key_video = f'EK-100/{video_id}.mp4'
    # upload_to_s3(video_path, bucket_name, s3_key_video)

# Main function
def main(inputs_csv, output_folder, tracking_file, bucket_name, strategy, splits_csv):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Initialize the URL builder based on the strategy
    if strategy == 'download':
        url_builder = EpicURLBuilder(epic_55_splits=splits_csv)
    elif strategy == 'local':
        url_builder = EpicURLBuilder("./torrents/epic-torrents/3h91syskeag572hl6tvuovwv4d", "./torrents/epic-torrents-1/2g1n6qdydwa9u22shpxqzp0t8m", epic_55_splits=splits_csv)
    else:
        raise ValueError("Invalid strategy. Choose either 'local' or 'download'.")

    # Load the original CSV file
    df = pd.read_csv(inputs_csv)

    # Load or initialize the tracking CSV
    if os.path.exists(tracking_file):
        tracking_df = pd.read_csv(tracking_file)
        df = df[~df['narration_id'].isin(tracking_df['narration_id'])]
    else:
        tracking_df = pd.DataFrame(columns=df.columns)

    # Group the dataframe by video_id
    grouped = df.groupby('video_id')
    
    # Create a lock for safe file writing
    lock = multiprocessing.Manager().Lock()

    # Process each group in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(process_video_group, video_id, group, output_folder, bucket_name, strategy, url_builder, lock, tracking_file)
            for video_id, group in grouped
        ]

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), leave=False):
            try:
                future.result()
            except Exception as e:
                print(f"{e}")

    # Update tracking
    # tracking_df = pd.concat([tracking_df, df], ignore_index=True)
    # tracking_df.to_csv(tracking_file, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Video Clipping and S3 Sync Tool")
    parser.add_argument('--inputs_csv', type=str, required=True, help='Path to the input CSV file.')
    parser.add_argument('--output_folder', type=str, required=True, help='Folder where the clips will be saved.')
    parser.add_argument('--tracking_file', type=str, required=True, help='Path to the tracking CSV file.')
    parser.add_argument('--bucket_name', type=str, required=True, help='The name of the S3 bucket to upload files to.')
    parser.add_argument('--strategy', type=str, choices=['local', 'download'], default='local',
                        help="Strategy to use for video retrieval: 'local' (default) or 'download'.")
    parser.add_argument('--splits_csv', type=str, required=True,
                        help="Path to the EPIC-55 splits CSV file or a URL to the file.")

    args = parser.parse_args()

    main(args.inputs_csv, args.output_folder, args.tracking_file, args.bucket_name, args.strategy, args.splits_csv)

# Example usage:
# pip3 install pandas tqdm requests moviepy boto3
# python3 download_and_clips_videos.py --inputs_csv ./EPIC_100_train.csv --output_folder processed_videos/clipped_videos --tracking_file ./data/training-clip-tracking.csv --bucket_name kumbi-dissertation --strategy local --splits_csv ./data/epic_55_splits.csv
# python3 download_and_clips_videos.py --inputs_csv ./EPIC_100_validation.csv --output_folder processed_videos/clipped_videos --tracking_file ./data/validation-clip-tracking.csv --bucket_name kumbi-dissertation --strategy local --splits_csv ./data/epic_55_splits.csv


#  python3 download_and_clips_videos.py --inputs_csv small_epic_example.csv --output_folder processed_videos/clipped_videos --tracking_file tracking.csv --bucket_name kumbi-dissertation --strategy local --splits_csv ./data/epic_55_splits.csv