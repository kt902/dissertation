import argparse
import pandas as pd
import os
import cv2
from pathlib import Path
import uuid  # For generating unique segment IDs
from tqdm import tqdm
import time
from augment import has_visor, load_annotations, find_nearest_annotations, overlay_mask, apply_occlusion, noun_class_colors
from decord import VideoReader, cpu
import math
from moviepy.editor import ImageSequenceClip
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor
import traceback

def frame_count_to_time_format(frame_count, fps=60):
    # Calculate total seconds from frame count
    total_seconds = frame_count / fps
    
    # Extract hours, minutes, and seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    
    # Calculate milliseconds
    milliseconds = int((total_seconds - int(total_seconds)) * 1000)
    
    # Format the time as '00:00:00.000'
    time_formatted = f'{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}'
    
    return time_formatted

def get_frame_count(row):
    return (row['stop_frame'] - row['start_frame'])

def generate_augmentation_plan(csv_path, original_root, plan_csv_path, augmented_segments_csv_path):
    # Load the original CSV
    data = pd.read_csv(csv_path)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(plan_csv_path), exist_ok=True)

    # Initialize a list to store augmentation plans
    plan_data = []
    new_rows_data = []

    # Function to generate a unique segment ID
    def generate_segment_id(narration_id):
        return f"{narration_id}_{uuid.uuid4().hex}"

    # Customizable strategy function
    def should_augment(row):
        # Define your strategy here; for example:
        # if row['verb_class'] in [0, 1, 2]:  # Example condition
        
        augmentations = [{'type': 'darken'}]
        
        if get_frame_count(row) > 120:
            augmentations.append({ 'type': 'completeness', 'params': {'level': 0.5} })
        if has_visor(row['video_id']):
            augmentations.append({ 'type': 'occlusion'})

        return True, augmentations # Return the augmentations to apply
        # return True, [{ 'type': 'occlusion'}]

    max_i = {}
    # Iterate through the original dataset
    for idx, row in data.iterrows():
        narration_id = row['narration_id']
        participant_id = row['participant_id']
        video_id = row['video_id']
        start_frame = row['start_frame']
        stop_frame = row['stop_frame']
        action_label = row['narration']  # Original action label

        # Determine whether to augment this segment and which augmentations to apply
        augment, augmentations = should_augment(row)

        if not augment:
            continue

        # Generate a unique segment ID
        # segment_id = generate_segment_id(narration_id)

        max_i[narration_id] = 0
        for i, augmentation in enumerate(augmentations):
            augment_type = augmentation['type']
            augment_params = augmentation.get('params', {})
            new_row = row.copy()
            segment_id =  narration_id + "_" + str(max_i[narration_id])
            max_i[narration_id] += 1
            
            new_row['narration_id'] = segment_id
            new_row['video_id'] = segment_id
            
            frame_count = get_frame_count(row)
            new_row['narration_timestamp'] = '00:00:00.000'
            new_row['start_timestamp'] = '00:00:00.000'
            new_row['start_frame'] = 1
            new_row['stop_frame'] = frame_count
            new_row['stop_timestamp'] = frame_count_to_time_format(frame_count)
            
# action_presence,camera_motion,lighting,focus,action_completeness,object_presence
            if augment_type == 'occlusion':
                new_row['object_presence'] = 1
            elif augment_type == 'completeness':
                frame_count = min(frame_count // 2, 60 * 3)
                new_row['action_completeness'] = 1
                new_row['stop_frame'] = frame_count
                new_row['stop_timestamp'] = frame_count_to_time_format(frame_count)

                augment_params['frame_count'] = frame_count

            elif augment_type == 'darken':
                new_row['lighting'] = 1
                

            # Example: Set augmentation-specific parameters

            # Record the augmentation plan
            plan_row = {
                'segment_id': segment_id,
                'narration_id': narration_id,
                'participant_id': participant_id,
                'video_id': video_id,
                'start_frame': start_frame,
                'stop_frame': stop_frame,
                'narration': action_label,
                'augment_type': augment_type,
                'augment_params': augment_params,
                # 'original_frame_dir': os.path.join(original_root, participant_id, video_id)
            }
            
            
            new_rows_data.append(new_row)
            plan_data.append(plan_row)

    negatives = add_negatives(data)
    
    for index, row in negatives.iterrows():
        narration_id = row['narration_id']
        participant_id = row['participant_id']
        video_id = row['video_id']
        start_frame = row['start_frame']
        stop_frame = row['stop_frame']
        action_label = row['narration']

        segment_id =  row['narration_id'] + "_" + str(max_i[narration_id])
        max_i[narration_id] += 1
        
        # Update narration id for uniqueness
        row['narration_id'] = segment_id
        
        plan_row = {
            'segment_id': segment_id,
            'narration_id': narration_id,
            'participant_id': participant_id,
            'video_id': video_id,
            'start_frame': start_frame,
            'stop_frame': stop_frame,
            'narration': action_label,
            'augment_type': 'negative',
            # The source of the annotation values is negative_narration_id
            'augment_params': {'negative_narration_id': row['negative_narration_id']},
        }
        plan_data.append(plan_row)
        new_rows_data.append(row)
    
    # Save the augmentation plan CSV
    plan_df = pd.DataFrame(plan_data)
    plan_df.to_csv(plan_csv_path, index=False)
    new_rows_df = pd.DataFrame(new_rows_data)
    new_rows_df = new_rows_df.drop('negative_narration_id', axis=1)

    
    
    # Define a function to calculate the quality score
    def calculate_quality_score(row):
        if row['action_presence'] == 0:
            return 0.0  # If action_presence is 0, the quality_score is 0

        quality_dimensions = ['camera_motion', 'lighting', 'focus', 'action_completeness', 'object_presence']

        # Avoid division by zero in case all quality dimensions are zero
        sum_of_inverses = sum(1.0 / row[dim] for dim in quality_dimensions if row[dim] != 0)
        
        if sum_of_inverses == 0:
            return 0.0  # If all dimensions are zero, return zero score

        # Calculate the harmonic mean of the quality dimensions
        harmonic_mean = len(quality_dimensions) / sum_of_inverses
        
        # Define the min and max values for the harmonic mean
        HM_min = 1  # The harmonic mean is at least 1 when all dimensions are equal to 1
        HM_max = 5  # The harmonic mean is at most 5 when all dimensions are equal to 5

        # Normalize the harmonic mean to a value between 0 and 1
        normalized_score = (harmonic_mean - HM_min) / (HM_max - HM_min)
        
        return normalized_score

        # Sum the weighted quality dimensions, assume equal weights for simplicity
        p = 1
        score = sum(row[dim] ** p for dim in quality_dimensions) / (len(quality_dimensions) ** (p + 1))
        return score
    

    new_rows_df = pd.concat([data, new_rows_df])

    # Calculate the quality score for each row in the quality data
    new_rows_df['quality_score'] = new_rows_df.apply(calculate_quality_score, axis=1)
    
    new_rows_df.to_csv(augmented_segments_csv_path, index=False)

    print(f"Augmentation plan saved to {plan_csv_path}")
    print(f"Augmented segments saved to {augmented_segments_csv_path}")


def add_negatives(df, negative_samples_count = 1):
    combined_group = df.groupby(['noun_class', 'verb_class'])
    # verb_group = df.groupby('verb_class')
    # noun_group = df.groupby('noun_class')
    
    # Initialize a cache dictionary
    cache = {}

    augmented_df = pd.DataFrame()
    # Step 2: Define a function to filter and cache the result
    def filter_and_cache(row, combined_group, cache):
        key = (row['noun_class'], row['verb_class'])
        
        # If the result is already cached, return it
        if key in cache:
            return cache[key]
        
        # Otherwise, filter the group and store it in the cache
        filtered_df = combined_group.filter(lambda x: x.name[0] != row['noun_class'] or x.name[1] != row['verb_class'])
        
        cache[key] = filtered_df
        return filtered_df
    
    for index, row in df.iterrows():
        # Sample n items from the filtered dataframe
        sampled_items = filter_and_cache(row, combined_group, cache).sample(n=negative_samples_count, random_state=np.random.RandomState())
        
        # Set quality_score to 0
        sampled_items['quality_score'] = 0
        sampled_items['action_presence'] = 0
        
        # Change noun_class and verb_class to match the parent record
        sampled_items['noun_class'] = row['noun_class']
        sampled_items['verb_class'] = row['verb_class']
        sampled_items['negative_narration_id'] = sampled_items['narration_id']
        sampled_items['narration_id'] = row['narration_id']
        
        augmented_df = pd.concat([augmented_df, sampled_items])
        
    return augmented_df


global annotations 
annotations = None
# Function to apply augmentations
def apply_augmentations(row, frame, frame_index, total_frames, frame_num, augment_type, params=None):
    global annotations 
    global noun_class_colors
    if augment_type == 'occlusion':
        # Apply occlusion logic (e.g., mask parts of the image)
        if annotations is None or annotations['video_id'] != row['video_id']:
            # TODO: add a flag for the root path ?
            annotations = {
                'video_id': row['video_id'],
                'annotations': load_annotations(row['video_id']),
            }

        frame_annotations = find_nearest_annotations(frame_num, annotations['annotations'])
        
        return apply_occlusion(frame, frame_annotations, noun_class_colors)
    elif augment_type == 'completeness':
        if frame_index > params['frame_count']:
            return None
        return frame
        # Apply action completeness logic (e.g., crop frames based on params)
        # pass
    elif augment_type == 'darken':
        # darker_frame = (frame * 0.3).astype(np.uint8)
        # return darker_frame
        
        gamma = 4.0
        normalized_frame = frame / 255.0
        # Apply gamma correction
        gamma_corrected_frame = np.power(normalized_frame, gamma)
        # Rescale back to [0, 255]
        darker_frame = (gamma_corrected_frame * 255).astype(np.uint8)
        return darker_frame
    elif augment_type == 'object_presence':
        # Apply object presence logic (e.g., blur specific objects)
        pass
    return frame

    
def process_augmentation_plan(plan_csv_path, augmented_root, progress_csv_path):
    # Load the augmentation plan
    plan_data = pd.read_csv(plan_csv_path)

    # Check if a progress CSV already exists to resume from where it left off
    if os.path.exists(progress_csv_path):
        progress_data = pd.read_csv(progress_csv_path)
    else:
        # Initialize the progress DataFrame if it doesn't exist
        progress_data = pd.DataFrame(columns=plan_data.columns.tolist() + ['status'])

    # Convert progress data to a dictionary for quick lookup
    completed_segments = set(progress_data[progress_data['status'] == 'completed']['segment_id'])

    # Ensure the output directory exists
    os.makedirs(augmented_root, exist_ok=True)

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(process_segment, augmented_root, row): row
            for idx, row in plan_data.iterrows() if row['segment_id'] not in completed_segments
        }
        
            # Iterate through the augmentation plan with segment-level progress tracking
        # for idx, row in tqdm(plan_data.iterrows(), total=len(plan_data), desc="Processing Segments"):

        with tqdm(total=len(futures), desc="Processing Segments") as pbar:
            # Use tqdm to track progress
            for future in as_completed(futures):
                try:
                    row = future.result(timeout=1*60)
                    # Mark as completed and add to progress tracking
                    row['status'] = 'completed'
                    progress_data = pd.concat([progress_data, pd.DataFrame([row])], ignore_index=True)

                    # Save progress after each completed segment to avoid data loss
                    progress_data.to_csv(progress_csv_path, index=False)
                    completed_segments.add(row['segment_id'])
                except Exception as e:
                    print(f"Error processing video: {e}")
                    raise e
                
                pbar.update(1)


    print(f"Augmentation processing completed. Progress saved to {progress_csv_path}")
    
def process_segment(augmented_root, row):
    segment_id = row['segment_id']

    # Skip segments that have already been completed
    # if segment_id in completed_segments:
    #   return row

    narration_id = row['narration_id']
    participant_id = row['participant_id']
    video_id = row['video_id']
    start_frame = row['start_frame']
    stop_frame = row['stop_frame']
    augment_type = row['augment_type']
    
    
    if augment_type == "negative":
        return row
    
    if isinstance(row['augment_params'], str):
        params = eval(row['augment_params'])  # Convert string back to dict if needed
    else:
        params = None

    # Directory to save augmented frames
    augmented_video_path = os.path.join(augmented_root, f"{segment_id}.mp4")
    Path(augmented_root).mkdir(parents=True, exist_ok=True)
    

    with open(f'../../processed_videos/clipped_resized_videos/{narration_id}.mp4', 'rb') as fid:
        # Load a video
        vr = VideoReader(fid, ctx=cpu(0))

        try:
            # Path to save videos
            # original_video_path = os.path.join(augment_dir, "original_video.mp4")

            # Initialize variables for VideoWriter
            # original_video_writer = None
            augmented_video_writer = None

            # Loop through the frames
            
            
            
            new_frames = []
            
            frames = vr.get_batch(range(0, len(vr) - 1))
            # `frame` is a decord NDArray, which can be converted to a numpy array
            # frames = [frame.asnumpy() for frame in frames]
            frames = frames.asnumpy()
            # print(len(frame_iterator), len(frames))
            
            # Can't use end_frame because FPS is not consistent
            frame_iterator = range(start_frame, start_frame + len(frames))
            total_frames = len(frame_iterator)
            
            # for (i, frame_num) in tqdm(enumerate(frame_iterator), desc=f"Segment {segment_id} [{augment_type}]", leave=False):
            for (i, frame_num) in enumerate(frame_iterator):
                frame = frames[i]
                # `frame` is a decord NDArray, which can be converted to a numpy array
                # frame = frame.asnumpy()
                # Convert the frame from BGR to RGB
                # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # original_frame_path = os.path.join(row['original_frame_dir'], f"frame_{frame_num:010}.jpg")
                # augmented_frame_path = os.path.join(augment_dir, f"frame_{frame_num:010}.jpg")

                # Read the original frame
                # frame = cv2.imread(original_frame_path)

                # Dynamically determine frame size and initialize VideoWriter (only on the first frame)
                # if augmented_video_writer is None:
                #     frame_size = (frame.shape[1], frame.shape[0])  # (Width, Height)
                #     fps = vr.get_avg_fps()  # Frames per second, adjust if necessary

                    # Initialize Video Writers for original and augmented videos
                    # original_video_writer = cv2.VideoWriter(original_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, frame_size)
                    # augmented_video_writer = cv2.VideoWriter(augmented_video_path, cv2.VideoWriter_fourcc('H','2','6','4'), fps, frame_size)

                # Apply the augmentation with the given parameters
                augmented_frame = apply_augmentations(row, frame, i, total_frames, frame_num, augment_type, params)

                # Save the augmented frame
                # cv2.imwrite(augmented_frame_path, augmented_frame)

                # Write frames to the video writers
                # original_video_writer.write(frame)
                # augmented_video_writer.write(frame)
                if augmented_frame is not None:
                    new_frames.append(augmented_frame)

            # Release the video writers
            # if augmented_video_writer is not None:
            #     augmented_video_writer.release()
            
            fps = vr.get_avg_fps()

            # Create a video clip from the frames (note that frames should be in RGB format for moviepy)
            clip = ImageSequenceClip(new_frames, fps=fps)

            # Write the video to a file
            clip.write_videofile(augmented_video_path, codec='libx264', fps=fps, logger=None)

            # Update tqdm with the current processing status

            # mark_completed(row, progress_data, completed_segments)
            # progress_data = mark_completed(row, progress_data, completed_segments)
            return row
        except Exception as e:
            # tqdm.write(f"Error processing segment {segment_id}: {e}")
            row['status'] = f'error: {e}'
            # traceback.print_stack()
            raise e

            progress_data = pd.concat([progress_data, pd.DataFrame([row])], ignore_index=True)
            progress_data.to_csv(progress_csv_path, index=False)

def main():
    parser = argparse.ArgumentParser(description="CLI for generating and processing video augmentations.")
    subparsers = parser.add_subparsers(dest="command")

    # Command for generating the augmentation plan
    generate_plan_parser = subparsers.add_parser('generate-plan', help="Generate an augmentation plan.")
    generate_plan_parser.add_argument('--csv-path', type=str, required=True, help="Path to the original CSV file.")
    generate_plan_parser.add_argument('--original-root', type=str, required=True, help="Path to the original video frames root directory.")
    generate_plan_parser.add_argument('--plan-csv-path', type=str, required=True, help="Path to save the generated augmentation plan CSV.")
    generate_plan_parser.add_argument('--augmented-segments-csv-path', type=str, required=True, help="Path to save the augmented segments CSV.")


    # Command for processing the augmentation plan
    process_plan_parser = subparsers.add_parser('process-plan', help="Process the augmentation plan.")
    process_plan_parser.add_argument('--progress-csv-path', type=str, required=True, help="Path to save the progress of augmentation processing.")
    process_plan_parser.add_argument('--plan-csv-path', type=str, required=True, help="Path to the augmentation plan CSV.")
    process_plan_parser.add_argument('--augmented-root', type=str, required=True, help="Root directory to save augmented frames.")

    args = parser.parse_args()

    if args.command == "generate-plan":
        generate_augmentation_plan(args.csv_path, args.original_root, args.plan_csv_path, args.augmented_segments_csv_path)
    elif args.command == "process-plan":
        process_augmentation_plan(args.plan_csv_path, args.augmented_root, args.progress_csv_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
