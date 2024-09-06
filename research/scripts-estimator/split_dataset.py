import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process model results")
    parser.add_argument('--augment', action=argparse.BooleanOptionalAction, required=False, help='With augmentations.')
    args = parser.parse_args()


    if args.augment:
        val_metadata_path = "/home/ec2-user/environment/my-dissertation/augmentation-pipeline/out/augmentated_segments.csv"
    else:
        val_metadata_path = "/home/ec2-user/environment/data-estimator/base_quality.csv"
    
    # Load the CSV files
    df = pd.read_csv(val_metadata_path)

    # Combine verb_class and noun_class for stratification purposes
    df['combined_class'] = df.apply(lambda row: f"{row['verb_class']}_{row['noun_class']}", axis=1)

    # Identify classes with fewer than 2 samples
    class_counts = df['combined_class'].value_counts()
    small_classes = class_counts[class_counts < 2].index.tolist()

    # Separate the small classes
    df_small_classes = df[df['combined_class'].isin(small_classes)]
    df = df[~df['combined_class'].isin(small_classes)]

    # Perform stratified split on the remaining data
    split = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=42)

    for train_val_idx, test_idx in split.split(df, df[['verb_class', 'noun_class', 'combined_class']]):
        train_val_set = df.iloc[train_val_idx]
        test_set = df.iloc[test_idx]

    # Further split train_val_set into train and validation sets
    split = StratifiedShuffleSplit(n_splits=1, test_size=0.25, random_state=42)  # 0.25 x 0.8 = 0.2

    # Identify classes with fewer than 2 samples
    class_counts = train_val_set['combined_class'].value_counts()
    small_classes = class_counts[class_counts < 2].index.tolist()

    # Separate the small classes
    df_small_classes_x = train_val_set[train_val_set['combined_class'].isin(small_classes)]
    train_val_set = train_val_set[~train_val_set['combined_class'].isin(small_classes)]

    for train_idx, val_idx in split.split(train_val_set, train_val_set[['verb_class', 'noun_class', 'combined_class']]):
        train_set = train_val_set.iloc[train_idx]
        val_set = train_val_set.iloc[val_idx]

    # Optionally add the small classes to the train set (or handle them as needed)
    train_set = pd.concat([train_set, df_small_classes_x, df_small_classes])

    print(len(train_set), len(val_set), len(test_set))
    # Save the splits to CSV files
    if args.augment:
        train_set.to_csv('/home/ec2-user/environment/data-estimator/base_all_train.csv', index=False)
        val_set.to_csv('/home/ec2-user/environment/data-estimator/base_all_val.csv', index=False)
        test_set.to_csv('/home/ec2-user/environment/data-estimator/base_all_test.csv', index=False)
    else:
        train_set.to_csv('/home/ec2-user/environment/data-estimator/base_train.csv', index=False)
        val_set.to_csv('/home/ec2-user/environment/data-estimator/base_val.csv', index=False)
        test_set.to_csv('/home/ec2-user/environment/data-estimator/base_test.csv', index=False)
