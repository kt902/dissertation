import pandas as pd

# Load the CSV files
quality_data = pd.read_csv('/home/ec2-user/environment/data-estimator/base_quality.csv')

# Define a function to calculate the quality score
def calculate_quality_score(row):
    if row['action_presence'] == 0:
        return 0.0  # If action_presence is 0, the quality_score is 0
    # Sum the weighted quality dimensions, assume equal weights for simplicity
    quality_dimensions = ['camera_motion', 'lighting', 'focus', 'action_completeness', 'object_presence']
    power = 3
    score = sum(row[dim]**power for dim in quality_dimensions) / (len(quality_dimensions) ** (1+power))
    return score

# Calculate the quality score for each row in the quality data
quality_data['quality_score'] = quality_data.apply(calculate_quality_score, axis=1)

quality_data.to_csv('/home/ec2-user/environment/data-estimator/aug_base_quality.csv', index=False)
