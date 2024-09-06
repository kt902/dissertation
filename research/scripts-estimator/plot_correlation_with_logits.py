import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Load your quality dataset
quality_data = pd.read_csv('/home/ec2-user/environment/data-estimator/model_results_with_logits.csv')

# Assuming the data already contains model performance metrics
# Merging is no longer necessary if everything is in the same file
merged_data = quality_data


# Now, calculate Spearman correlations between model performance and quality dimensions
correlation_results = {}

# Specify the model performance metrics you're interested in
performance_metrics = [
    'tsn_raw_logit_verb',
    'tsn_raw_logit_noun',
    'tsn_raw_logit_action',
    'avion_raw_logit_verb',
    'avion_raw_logit_noun',
        'avion_raw_logit_action'
]

# Specify the quality dimensions
quality_dimensions = [
    'quality_score', 'camera_motion', 'lighting', 'focus', 'action_completeness', 'object_presence'
]

merged_data.loc[merged_data['action_presence'] == 0, quality_dimensions] = 0.0


# Calculate Spearman correlations for each performance metric against each quality dimension
for metric in performance_metrics:
    # Select only the relevant columns, drop any rows with NaN values
    selected_data = merged_data[quality_dimensions + [metric]].dropna()

    # Calculate Spearman correlation
    if not selected_data.empty and selected_data[metric].nunique() > 1:
        # Calculate correlation only if there are at least 2 unique values
        correlation = selected_data.corr(method='spearman')
        correlation_results[metric] = correlation[metric].drop(metric)
    else:
        # Handle cases where correlation cannot be computed (e.g., constant columns)
        correlation_results[metric] = pd.Series([0] * len(quality_dimensions), index=quality_dimensions)


# Convert the correlation results into a DataFrame for easier visualization
correlation_df = pd.DataFrame(correlation_results)

# Visualize the correlations using a heatmap

plt.figure(figsize=(12, 8))
# Create the heatmap with enhanced labels
label_mapping = {
    'action_completeness': 'Action Completeness',
    'action_presence': 'Action Presence',
    'camera_motion': 'Camera Motion',
    'lighting': 'Lighting',
    'focus': 'Focus',
    'object_presence': 'Object Presence',
    'quality_score': 'Quality Score',
    'tsn_raw_logit_verb': 'Verb Logit',
    'tsn_raw_logit_noun': 'Noun Logit',
    'tsn_raw_logit_action': 'Action Logit',
    'avion_raw_logit_action': 'Action Logit',
    'avion_raw_logit_verb': 'Verb Logit',
    'avion_raw_logit_noun': 'Noun Logit'
}

correlation_df = correlation_df.rename(index=label_mapping, columns=label_mapping)

# Plot the heatmap
ax = sns.heatmap(
    correlation_df,
    annot=True,
    cmap='coolwarm',
    center=0,
    cbar_kws={"shrink": .8},
    linewidths=.5,
    linecolor='black'
)

# Set the title and labels
plt.title('Spearman Correlation of Model Performance vs Video Segment Quality', fontsize=14, y = 1.1)
ax.set_ylabel('Video Segment Quality', fontsize=12)
ax.set_xlabel('Action Recognition Model (Raw Logit) Performance', fontsize=12)

# Enhance the x-axis labels
performance_metrics = correlation_df.columns
ax.set_xticklabels(performance_metrics, rotation=45, ha='right', fontsize=10)

print(correlation_df.columns)
# Add divider to separate TSN and AVION
divider_position = len(correlation_df.columns) / 2

# Draw a vertical line to separate TSN and AVION columns
ax.axvline(x=divider_position, color='black', linewidth=2.5)

# Add divider to separate TSN and AVION
# divider_position = len(correlation_df.columns) / 2

# Draw a horizontal line to separate dimentations and quality score
ax.axhline(y=1, color='black', linewidth=2.5)

# Optionally, add labels above the x-axis to indicate TSN and AVION sections
ax.text(divider_position / 2, -0.3, 'TSN', ha='center', va='center', fontsize=12, fontweight='bold')
ax.text(divider_position + (len(performance_metrics) - divider_position) / 2, -0.3, 'AVION', ha='center', va='center', fontsize=12, fontweight='bold')

# Save the enhanced heatmap
plt.tight_layout()
plt.savefig('/home/ec2-user/environment/figures/logits_spearman_correlation_heatmap.pdf')

# Optionally, you can visualize specific correlations with scatter plots
# for metric in performance_metrics:
#     for dimension in quality_dimensions:
#         plt.figure()
#         sns.scatterplot(data=merged_data, x=dimension, y=metric)
#         plt.title(f'Scatter plot of {metric} vs {dimension} (Spearman)')
#         plt.xlabel(dimension)
#         plt.ylabel(metric)
#         plt.grid(True)
#         plt.savefig(f'figures/logits_scatter_{metric}_vs_{dimension}.png')

# Save the correlation dataframe to a CSV file for reference
correlation_df.to_csv('/home/ec2-user/environment/figures/model_performance_quality_correlation_spearman.csv')


# ------ other

quality_dimensions = [q for q in quality_dimensions if q != "action_presence" and q != "quality_score"]

correlation_results = {}
# Calculate Spearman correlations for each performance metric against each quality dimension
selected_data = merged_data[quality_dimensions + ['quality_score']].dropna()
correlation = selected_data.corr(method='pearson')
correlation_results['quality_score'] = correlation['quality_score'].drop('quality_score')
# Convert the correlation results into a DataFrame for easier visualization
correlation_df = pd.DataFrame(correlation_results)

# Visualize the correlations using a heatmap

plt.figure(figsize=(12, 8))
# Create the heatmap with enhanced labels

correlation_df = correlation_df.rename(index=label_mapping, columns=label_mapping)

# Plot the heatmap
ax = sns.heatmap(
    correlation_df,
    annot=True,
    cmap='coolwarm',
    center=0,
    cbar_kws={"shrink": .8},
    linewidths=.5,
    linecolor='black'
)

# Set the title and labels
plt.title('Spearman Correlation of Quality Score vs Other Dimensions')
# plt.xlabel('Quality Dimensions')
# plt.ylabel('Correlation with Quality Score')

# Rotate the y-axis labels to ensure they fit
plt.yticks(rotation=0)
plt.xticks(rotation=45, ha='right')

# Save the plot to the 'figures' folder
plt.tight_layout()
plt.savefig('/home/ec2-user/environment/figures/logits_quality_score_vs_dimensions_correlation_heatmap.png')



# Plot scatter plots for each dimension vs. quality_score

# Define the number of rows and columns for the subplots grid
n_cols = 2
n_rows = int(np.ceil(len(quality_dimensions) / n_cols))

# Create a figure and a grid of subplots
fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 8))

# Flatten the axes array for easy iteration (in case you have a grid)
axes = axes.flatten()

# Plot each dimension on a separate subplot
for i, dimension in enumerate(quality_dimensions):
    sns.boxplot(x=merged_data[dimension], y=merged_data['quality_score'], ax=axes[i])
    axes[i].set_title(f'Quality Score vs {label_mapping.get(dimension, dimension)}')
    axes[i].set_xlabel(label_mapping.get(dimension, dimension))
    axes[i].set_ylabel('Quality Score')
    axes[i].grid(True)

# Hide any unused subplots (if n_rows * n_cols > len(quality_dimensions))
for j in range(i + 1, len(axes)):
    axes[j].axis('off')

# Adjust layout and save the figure
plt.tight_layout()
plt.savefig('/home/ec2-user/environment/figures/logits_quality_score_vs_dimensions_boxplots.png')
