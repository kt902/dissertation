import pandas as pd

# Load the CSV files
quality_data = pd.read_csv('/home/ec2-user/environment/data/manual_annotations_from_ui.csv')
ground_truth_data = pd.read_csv('/home/ec2-user/environment/data-estimator/manual_annotations_raw_dataset.csv')

# Define a function to calculate the quality score
def calculate_quality_score(row):
    if row['action_presence'] == 0:
        return 0.0  # If action_presence is 0, the quality_score is 0
    # Sum the weighted quality dimensions, assume equal weights for simplicity
    quality_dimensions = ['camera_motion', 'lighting', 'focus', 'action_completeness', 'object_presence']
    score = sum(row[dim] for dim in quality_dimensions) / (5 * len(quality_dimensions))
    return score

# Calculate the quality score for each row in the quality data
quality_data['quality_score'] = quality_data.apply(calculate_quality_score, axis=1)

# Merge the quality data with the ground truth data on narration_id
merged_data = pd.merge(quality_data, ground_truth_data, on='narration_id')

# Select the relevant columns for the output
output_columns = [
    'narration_id', 'participant_id_x', 'video_id_x', 'narration_timestamp',
    'start_timestamp', 'stop_timestamp', 'start_frame', 'stop_frame', 'narration',
    'verb', 'verb_class', 'noun', 'noun_class', 'all_nouns', 'all_noun_classes',
    'sequence_id', 
    'camera_motion', 'lighting', 'focus', 'action_completeness', 'object_presence',
    'quality_score'
]

# Rename columns to match the expected output
merged_data = merged_data[output_columns]
merged_data.columns = [
    'narration_id', 'participant_id', 'video_id', 'narration_timestamp',
    'start_timestamp', 'stop_timestamp', 'start_frame', 'stop_frame', 'narration',
    'verb', 'verb_class', 'noun', 'noun_class', 'all_nouns', 'all_noun_classes',
    'sequence_id',
    'camera_motion', 'lighting', 'focus', 'action_completeness', 'object_presence',
    'quality_score'
]

# Save the output to a new CSV file
merged_data.to_csv('/home/ec2-user/environment/data-estimator/data-estimator/base_quality_with_duplicates.csv', index=False)

print("Output CSV file '/home/ec2-user/environment/data-estimator/base_quality_with_duplicates.csv' generated successfully.")
