import pandas as pd
import numpy as np

new_df = pd.read_csv('/home/ec2-user/environment/data-estimator/base_train.csv')
# other_df = pd.read_csv('/home/ec2-user/environment/AVION/datasets/EK100/epic-kitchens-100-annotations/EPIC_100_train.csv')

other_df = new_df
combined_group = other_df.groupby(['noun_class', 'verb_class'])
verb_group = other_df.groupby('verb_class')
noun_group = other_df.groupby('noun_class')

# Step 3: For each record in the new CSV, generate negative examples
augmented_df = new_df

# Initialize a cache dictionary
cache = {}

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

for index, row in new_df.iterrows():
    # Sample n items from the filtered dataframe
    # filtered_df = filter_and_cache(row, combined_group, cache)
    
    sampled_items = filter_and_cache(row, combined_group, cache).sample(n=2, random_state=np.random.RandomState())
    
    # Set quality_score to 0
    sampled_items['quality_score'] = 0
    sampled_items['action_presence'] = 0
    
    # Change noun_class and verb_class to match the parent record
    sampled_items['noun_class'] = row['noun_class']
    sampled_items['verb_class'] = row['verb_class']
    
    augmented_df = pd.concat([augmented_df, sampled_items])

# Step 4: Convert the augmented data to a DataFrame

# print(augmented_df)
# Step 5: Save the augmented DataFrame to a new CSV file
augmented_df.to_csv('/home/ec2-user/environment/data-estimator/train.csv', index=False)


# from src.datasets import EpicVideoDataset
# from pathlib import Path

# d = EpicVideoDataset(Path("./rgb_train"))
# print(len(d.video_records))