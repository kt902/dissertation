import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load your datasets
train_data = pd.read_csv('/home/ec2-user/environment/AVION/datasets/EK100/epic-kitchens-100-annotations/EPIC_100_train.csv')
validation_data = pd.read_csv('/home/ec2-user/environment/AVION/datasets/EK100/epic-kitchens-100-annotations/EPIC_100_validation.csv')

complete_data = pd.concat([train_data, validation_data], ignore_index=True)
augmented_quality_data = pd.read_csv('/home/ec2-user/environment/my-dissertation/augmentation-pipeline/out/augmentated_segments.csv')
quality_data = pd.read_csv('/home/ec2-user/environment/data-estimator/base_quality.csv')
train_data = pd.read_csv('/home/ec2-user/environment/data-estimator/base_all_train.csv')
val_data = pd.read_csv('/home/ec2-user/environment/data-estimator/base_all_val.csv')
test_data = pd.read_csv('/home/ec2-user/environment/data-estimator/base_all_test.csv')

# Add a column to identify the dataset
complete_data['dataset'] = 'complete'
augmented_quality_data['dataset'] = 'augmented'
# quality_data['dataset'] = 'quality'
train_data['dataset'] = 'train'
val_data['dataset'] = 'validation'
test_data['dataset'] = 'test'

# Combine all data into one DataFrame
combined_data = pd.concat([augmented_quality_data, quality_data, train_data, val_data, test_data])

# Count the number of instances for each participant in each dataset
participant_counts = combined_data.groupby(['participant_id', 'dataset']).size().reset_index(name='count')

# Plot the representation of participants across datasets
plt.figure(figsize=(12, 6))
sns.barplot(x='participant_id', y='count', hue='dataset', data=participant_counts)
plt.title('Participant Representation Across Splits')
plt.xlabel('Participant ID')
plt.ylabel('Number of Instances')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('/home/ec2-user/environment/figures/participant_representation.png')
plt.close()

# Function to get top 20 classes
def get_top_classes(df, class_column, top_n=20):
    # Count instances per class
    class_counts = df[df['dataset'] == 'quality'][class_column].value_counts().nlargest(top_n)
    # Filter dataset to include only top classes
    return df[df[class_column].isin(class_counts.index)]


# Create a figure with 3 subplots, one for each class type (verb, noun, action)
fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

# --- Verb Class Representation
verb_class_filtered = get_top_classes(combined_data, 'verb_class')
verb_class_counts = verb_class_filtered.groupby(['verb_class', 'dataset']).size().reset_index(name='count')
sns.barplot(x='verb_class', y='count', hue='dataset', data=verb_class_counts, ax=axes[0])
axes[0].set_title('Top 20 Verb Classes Representation Across Splits')
axes[0].set_xlabel('Verb Class')
axes[0].set_ylabel('Number of Instances')

# --- Noun Class Representation
noun_class_filtered = get_top_classes(combined_data, 'noun_class')
noun_class_counts = noun_class_filtered.groupby(['noun_class', 'dataset']).size().reset_index(name='count')
sns.barplot(x='noun_class', y='count', hue='dataset', data=noun_class_counts, ax=axes[1])
axes[1].set_title('Top 20 Noun Classes Representation Across Splits')
axes[1].set_xlabel('Noun Class')
axes[1].set_ylabel('Number of Instances')

# --- Action Class Representation
# Assuming action_class is represented by the combination of verb_class and noun_class
combined_data['action_class'] = combined_data['verb_class'].astype(str) + '_' + combined_data['noun_class'].astype(str)
action_class_filtered = get_top_classes(combined_data, 'action_class')
action_class_counts = action_class_filtered.groupby(['action_class', 'dataset']).size().reset_index(name='count')
sns.barplot(x='action_class', y='count', hue='dataset', data=action_class_counts, ax=axes[2])
axes[2].set_title('Top 20 Action Classes Representation Across Splits')
axes[2].set_xlabel('Action Class')
axes[2].set_ylabel('Number of Instances')

# Rotate x-axis labels for better readability
for ax in axes:
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

plt.tight_layout()
plt.savefig('/home/ec2-user/environment/figures/top20_class_representation_across_splits.png')
plt.close()

# Repeat similarly for noun_class and action_class

# Verb, noun, and action class counts
class_counts = pd.concat([train_data, val_data, test_data, quality_data, augmented_quality_data, complete_data]).groupby(['dataset']).agg({
    'verb_class': 'nunique',
    'noun_class': 'nunique',
    'narration_id': 'count'  # Assuming narration_id represents action_class
}).reset_index()

class_counts.columns = ['Dataset', 'Unique Verb Classes', 'Unique Noun Classes', 'Total Video Segments']

print(class_counts)

# Optionally, save as a CSV file
class_counts.to_csv('/home/ec2-user/environment/figures/class_counts_summary.csv', index=False)

# Rename the 'dataset' column to 'Dataset Split'
combined_data.rename(columns={'dataset': 'Dataset Split'}, inplace=True)

# Define a mapping for your dataset labels if needed
dataset_label_mapping = {
    'augmented': 'Annotated Quality Dataset with Augmentations',
    'quality': 'Annotated Quality Dataset',
    'train': 'Training Set',
    'validation': 'Validation Set',
    'test': 'Test Set'
}

combined_data['Dataset Split'] = combined_data['Dataset Split'].map(dataset_label_mapping)


# Apply the label mapping
sns.histplot(data=combined_data, x='quality_score', hue='Dataset Split', kde=True, multiple="stack", bins=30)

# Set plot title and labels
plt.title('Distribution of Quality Score across Annotated Quality Dataset')
plt.xlabel('Quality Score')
plt.ylabel('Frequency')

# Save the plot to a file
plt.tight_layout()
plt.savefig('/home/ec2-user/environment/figures/quality_score_distribution.pdf')
plt.close()
