import pandas as pd
import argparse

def check_narration_id_uniqueness(csv_file1, csv_file2):
    """
    Check for unique narration_id across two CSV files.
    
    :param csv_file1: Path to the first CSV file.
    :param csv_file2: Path to the second CSV file.
    """
    # Load the CSV files into DataFrames
    df1 = pd.read_csv(csv_file1)
    df2 = pd.read_csv(csv_file2)
    
    # Check if both files have the `narration_id` column
    if 'narration_id' not in df1.columns or 'narration_id' not in df2.columns:
        raise ValueError("Both CSV files must contain a 'narration_id' column.")
    
    # Find overlapping narration_ids
    overlapping_narration_ids = set(df1['narration_id']).intersection(set(df2['narration_id']))
    
    if overlapping_narration_ids:
        print(f"Found {len(overlapping_narration_ids)} duplicate narration_ids across the two files.")
        print("Duplicate narration_ids:", overlapping_narration_ids)
    else:
        print("No duplicate narration_ids found. All narration_id values are unique across both files.")

def merge_and_remove_duplicates(csv_file1, csv_file2, output_file):
    """
    Merge two CSV files and remove any duplicate rows based on the 'narration_id' column.
    
    :param csv_file1: Path to the first CSV file.
    :param csv_file2: Path to the second CSV file.
    :param output_file: Path to the output CSV file where the merged result will be saved.
    """
    # Load the CSV files into DataFrames
    df1 = pd.read_csv(csv_file1)
    df2 = pd.read_csv(csv_file2)
    
    # Check if both files have the `narration_id` column
    if 'narration_id' not in df1.columns or 'narration_id' not in df2.columns:
        raise ValueError("Both CSV files must contain a 'narration_id' column.")
    
    # Merge the DataFrames and drop duplicates
    merged_df = pd.concat([df1, df2]).drop_duplicates(subset='narration_id', keep='first')
    
    # Save the merged DataFrame to the output file
    merged_df.to_csv(output_file, index=False)
    print(f"Merged file saved to {output_file} with {len(merged_df)} unique records.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check narration_id uniqueness or merge two CSV files while removing duplicates.")
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Choose a command to run.")
    
    # Subparser for checking uniqueness
    parser_check = subparsers.add_parser("check", help="Check for unique narration_id across two CSV files.")
    parser_check.add_argument("--csv_file1", type=str, required=True, help="Path to the first CSV file.")
    parser_check.add_argument("--csv_file2", type=str, required=True, help="Path to the second CSV file.")
    
    # Subparser for merging and removing duplicates
    parser_merge = subparsers.add_parser("merge", help="Merge two CSV files and remove duplicates based on narration_id.")
    parser_merge.add_argument("--csv_file1", type=str, required=True, help="Path to the first CSV file.")
    parser_merge.add_argument("--csv_file2", type=str, required=True, help="Path to the second CSV file.")
    parser_merge.add_argument("--output_file", type=str, required=True, help="Path to the output CSV file.")

    args = parser.parse_args()
    
    if args.command == "check":
        check_narration_id_uniqueness(args.csv_file1, args.csv_file2)
    elif args.command == "merge":
        merge_and_remove_duplicates(args.csv_file1, args.csv_file2, args.output_file)
