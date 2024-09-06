import pandas as pd

# Load the CSV files
ground_truth_data = pd.read_csv('/home/ec2-user/environment/data-estimator/manual_annotations_raw_dataset.csv')
quality_data = pd.read_csv('/home/ec2-user/environment/data/manual_annotations_from_ui.csv')
quality_data = quality_data.drop('participant_id', axis=1)
quality_data = quality_data.drop('video_id', axis=1)

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

# Calculate the quality score for each row in the quality data
quality_data['quality_score'] = quality_data.apply(calculate_quality_score, axis=1)

quality_data = quality_data.groupby('narration_id', as_index=False).agg({
    # 'participant_id': 'first',  # You can keep the first occurrence for non-quality_score columns
    # 'video_id': 'first',
    'action_presence': 'first',
    'camera_motion': 'first',
    'lighting': 'first',
    'focus': 'first',
    'action_completeness': 'first',
    'object_presence': 'first',
    'quality_score': 'mean'  # Take the mean of quality_score for duplicates
})

print(len(quality_data))
print(quality_data['narration_id'].is_unique)

# Merge the quality data with the ground truth data on narration_id
merged_data = pd.merge(quality_data, ground_truth_data, on='narration_id')


# Select the relevant columns for the output
output_columns = [
    'narration_id',  'participant_id', 'video_id', 'narration_timestamp',
    'start_timestamp', 'stop_timestamp', 'start_frame', 'stop_frame', 'narration',
    'verb', 'verb_class', 'noun', 'noun_class', 'all_nouns', 'all_noun_classes',
    'sequence_id',
    'action_presence', 'camera_motion', 'lighting', 'focus', 'action_completeness', 'object_presence',
    'quality_score'
]

# Rename columns to match the expected output
merged_data = merged_data[output_columns]
# merged_data.columns = [
#     'narration_id', 'participant_id', 'video_id', 'narration_timestamp',
#     'start_timestamp', 'stop_timestamp', 'start_frame', 'stop_frame', 'narration',
#     'verb', 'verb_class', 'noun', 'noun_class', 'all_nouns', 'all_noun_classes',
#     'sequence_id',
#     'camera_motion', 'lighting', 'focus', 'action_completeness', 'object_presence',
#     'quality_score'
# ]

# Start the split
df = merged_data
df = df.drop('sequence_id', axis=1)

df.to_csv('/home/ec2-user/environment/data-estimator/base_quality.csv', index=False)
