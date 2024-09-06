import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error

# Create directory for figures if it doesn't exist
figures_dir = './estimator-figures'
if not os.path.exists(figures_dir):
    os.makedirs(figures_dir)

# Load the model results
with open("/home/ec2-user/environment/C1-Action-Recognition-TSN-TRN-TSM/results/finetune_results.pt", "rb") as f:
    model_results = pickle.load(f)

# Load the test set and quality dataset for statistics
test_data = pd.read_csv('/home/ec2-user/environment/data-estimator/base_all_test.csv')
quality_data = pd.read_csv('/home/ec2-user/environment/my-dissertation/augmentation-pipeline/out/augmentated_segments.csv')
# Merge with model results on narration_id to get the predictions
merged_data = pd.merge(test_data, pd.DataFrame(model_results), on='narration_id')

# Calculate MAE for each example
merged_data['MAE'] = np.abs(merged_data['quality_score'] - merged_data['output'])

# Global average statistics
global_avg_mae = merged_data['MAE'].mean()
global_avg_quality = merged_data['quality_score'].mean()
global_avg_predicted = merged_data['output'].mean()

print(f"Global Average MAE: {global_avg_mae:.4f}")
print(f"Global Average Quality Score: {global_avg_quality:.4f}")
print(f"Global Average Predicted Score: {global_avg_predicted:.4f}")

# Averages and statistics by noun_class
noun_class_stats = merged_data.groupby('noun_class').agg({
    'MAE': ['mean'],
    'quality_score': ['mean'],
    'output': ['mean'],
    'narration_id': 'count'
}).reset_index()
noun_class_stats.columns = ['noun_class', 'avg_mae', 'avg_quality_score', 'avg_output', 'count']
noun_class_stats = noun_class_stats.sort_values(by='count', ascending=False)

# Averages and statistics by verb_class
verb_class_stats = merged_data.groupby('verb_class').agg({
    'MAE': ['mean'],
    'quality_score': ['mean'],
    'output': ['mean'],
    'narration_id': 'count'
}).reset_index()
verb_class_stats.columns = ['verb_class', 'avg_mae', 'avg_quality_score', 'avg_output', 'count']
verb_class_stats = verb_class_stats.sort_values(by='count', ascending=False)

# Save the statistics to CSV files for further analysis
noun_class_stats.to_csv(os.path.join(figures_dir, 'noun_class_statistics_mae.csv'), index=False)
verb_class_stats.to_csv(os.path.join(figures_dir, 'verb_class_statistics_mae.csv'), index=False)

# Plotting: MAE for each example
plt.figure(figsize=(10, 6))
plt.plot(merged_data.index, merged_data['MAE'], marker='o', linestyle='-', color='b')
plt.xlabel('Example Index')
plt.ylabel('Mean Absolute Error (MAE)')
plt.title('MAE for Each Example')
plt.grid(True)
plt.savefig(os.path.join(figures_dir, 'mae_plot.pdf'))

# Plotting: MAE by Noun Class
plt.figure(figsize=(10, 6))
plt.bar(noun_class_stats['noun_class'], noun_class_stats['avg_mae'], color='orange')
plt.xlabel('Noun Class')
plt.ylabel('Average MAE')
plt.title('Average MAE by Noun Class')
plt.grid(True)
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, 'avg_mae_by_noun_class.pdf'))

# Plotting: MAE by Verb Class
plt.figure(figsize=(10, 6))
plt.bar(verb_class_stats['verb_class'], verb_class_stats['avg_mae'], color='green')
plt.xlabel('Verb Class')
plt.ylabel('Average MAE')
plt.title('Average MAE by Verb Class')
plt.grid(True)
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, 'avg_mae_by_verb_class.pdf'))

# Plotting: Quality Score vs Predicted Output (Overall)
plt.figure(figsize=(10, 6))
plt.scatter(merged_data['quality_score'], merged_data['output'], alpha=0.6)
plt.xlabel('True Quality Score')
plt.ylabel('Predicted Output')
plt.title('Quality Score vs Predicted Output')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, 'quality_vs_predicted_output.pdf'))

# Summary: Verb Class vs Noun Class Averages
verb_noun_summary = merged_data.groupby(['verb_class', 'noun_class']).agg({
    'MAE': ['mean'],
    'quality_score': ['mean'],
    'output': ['mean']
}).reset_index()
verb_noun_summary.columns = ['verb_class', 'noun_class', 'avg_mae', 'avg_quality_score', 'avg_output']
verb_noun_summary = verb_noun_summary.sort_values(by='avg_mae', ascending=False)
verb_noun_summary.to_csv(os.path.join(figures_dir, 'verb_noun_class_summary_mae.csv'), index=False)

# Print key statistics
print("\nKey Statistics:")
print(f"Global Average MAE: {global_avg_mae:.4f}")
print(f"Global Average Quality Score: {global_avg_quality:.4f}")
print(f"Global Average Predicted Score: {global_avg_predicted:.4f}")
print(f"\nTop 5 Noun Classes by Count:")
print(noun_class_stats.head(5))
print(f"\nTop 5 Verb Classes by Count:")
print(verb_class_stats.head(5))
