import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Create the figures directory if it doesn't exist
figures_dir = '/home/ec2-user/environment/tmp-figures'
if not os.path.exists(figures_dir):
    os.makedirs(figures_dir)

# Load the quality dataset
quality_data = pd.read_csv('/home/ec2-user/environment/data-estimator/model_results_with_logits.csv')

# Assuming the data already contains model performance metrics
merged_data = quality_data

# Function to calculate correlations for a given subset of data
def calculate_and_plot_correlations(subset, title_suffix, file_suffix):
    correlation_results = {}
    
    # Specify the model performance metrics and quality dimensions
    performance_metrics = [
        'tsn_raw_logit_verb', 'tsn_raw_logit_noun', 'tsn_raw_logit_action',
        'avion_raw_logit_verb', 'avion_raw_logit_noun', 'avion_raw_logit_action'
    ]
    
    quality_dimensions = [
        'quality_score', 'camera_motion', 'lighting', 'focus', 'action_completeness', 'object_presence'
    ]
    
    # Set to 0 when action presence is 0
    subset.loc[subset['action_presence'] == 0, quality_dimensions] = 0.0
    
    # Calculate Spearman correlations for each performance metric against each quality dimension
    for metric in performance_metrics:
        selected_data = subset[quality_dimensions + [metric]].dropna()

        if not selected_data.empty and selected_data[metric].nunique() > 1:
            correlation = selected_data.corr(method='spearman')
            correlation_results[metric] = correlation[metric].drop(metric)
        else:
            correlation_results[metric] = pd.Series([0] * len(quality_dimensions), index=quality_dimensions)
    
    # Convert the correlation results into a DataFrame for easier visualization
    correlation_df = pd.DataFrame(correlation_results)

    # Enhanced label mapping for better readability
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
        'avion_raw_logit_verb': 'Verb Logit',
        'avion_raw_logit_noun': 'Noun Logit',
        'avion_raw_logit_action': 'Action Logit'
    }

    # Rename for better visualization
    correlation_df = correlation_df.rename(index=label_mapping, columns=label_mapping)

    # Plot the heatmap
    plt.figure(figsize=(12, 8))
    ax = sns.heatmap(
        correlation_df,
        annot=True,
        cmap='coolwarm',
        center=0,
        cbar_kws={"shrink": .8},
        linewidths=.5,
        linecolor='black'
    )

    plt.title(f'Spearman Correlation of Model Performance vs Video Segment Quality ({title_suffix})', fontsize=14)
    ax.set_ylabel('Video Segment Quality', fontsize=12)
    ax.set_xlabel('Action Recognition Model (Raw Logit) Performance', fontsize=12)

    # Enhance the x-axis labels
    ax.set_xticklabels(correlation_df.columns, rotation=45, ha='right', fontsize=10)

    # Add a divider between TSN and AVION columns
    divider_position = len(correlation_df.columns) / 2
    ax.axvline(x=divider_position, color='black', linewidth=2.5)

    # Add horizontal line to separate dimensions
    ax.axhline(y=1, color='black', linewidth=2.5)

    # Add TSN and AVION labels
    ax.text(divider_position / 2, -0.3, 'TSN', ha='center', va='center', fontsize=12, fontweight='bold')
    ax.text(divider_position + (len(performance_metrics) - divider_position) / 2, -0.3, 'AVION', ha='center', va='center', fontsize=12, fontweight='bold')

    # Save the heatmap
    plt.tight_layout()
    plt.savefig(f'{figures_dir}/logits_spearman_correlation_heatmap_{file_suffix}.pdf')

    # Return the correlation dataframe (for reporting purposes)
    return correlation_df

# ---- Split the data by noun_class and verb_class frequency ----

# Rank noun_class by frequency
noun_class_counts = merged_data['noun_class'].value_counts()
top_noun_classes = noun_class_counts.index[:int(0.2 * len(noun_class_counts))]  # Top 20%
bottom_noun_classes = noun_class_counts.index[-int(0.2 * len(noun_class_counts)):]  # Bottom 20%

# Rank verb_class by frequency
verb_class_counts = merged_data['verb_class'].value_counts()
top_verb_classes = verb_class_counts.index[:int(0.2 * len(verb_class_counts))]  # Top 20%
bottom_verb_classes = verb_class_counts.index[-int(0.2 * len(verb_class_counts)):]  # Bottom 20%

# Subsets for analysis
top_noun_subset = merged_data[merged_data['noun_class'].isin(top_noun_classes)]
bottom_noun_subset = merged_data[merged_data['noun_class'].isin(bottom_noun_classes)]
top_verb_subset = merged_data[merged_data['verb_class'].isin(top_verb_classes)]
bottom_verb_subset = merged_data[merged_data['verb_class'].isin(bottom_verb_classes)]

# ---- Run correlations for each subset ----

# Top Noun Classes
top_noun_corr_df = calculate_and_plot_correlations(
    top_noun_subset, title_suffix="Top 20% Noun Classes", file_suffix="top_noun"
)

# Bottom Noun Classes
bottom_noun_corr_df = calculate_and_plot_correlations(
    bottom_noun_subset, title_suffix="Bottom 20% Noun Classes", file_suffix="bottom_noun"
)

# Top Verb Classes
top_verb_corr_df = calculate_and_plot_correlations(
    top_verb_subset, title_suffix="Top 20% Verb Classes", file_suffix="top_verb"
)

# Bottom Verb Classes
bottom_verb_corr_df = calculate_and_plot_correlations(
    bottom_verb_subset, title_suffix="Bottom 20% Verb Classes", file_suffix="bottom_verb"
)

# Optionally, you can save these correlation dataframes for further analysis
top_noun_corr_df.to_csv(f'{figures_dir}/top_noun_classes_correlation.csv')
bottom_noun_corr_df.to_csv(f'{figures_dir}/bottom_noun_classes_correlation.csv')
top_verb_corr_df.to_csv(f'{figures_dir}/top_verb_classes_correlation.csv')
bottom_verb_corr_df.to_csv(f'{figures_dir}/bottom_verb_classes_correlation.csv')

