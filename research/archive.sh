#!/bin/bash

# Check if source directory is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <source_directory>"
  exit 1
fi

# Create the archives directory if it doesn't exist
if [ ! -d "archives" ]; then
  mkdir archives
fi

# Get the current date in YYYY-MM-DD_HH-MM-SS format
current_date=$(date +"%Y-%m-%d_%H-%M-%S")

# Copy the folder to the archives directory with the date
mkdir -p "archives/${current_date}"
cp -R "$1" "archives/${current_date}/$(basename "$1")"

# Print a success message
echo "Archived $1 to archives/${current_date}/$(basename "$1")"
