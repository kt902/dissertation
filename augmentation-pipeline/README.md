# Video Segment Augmentation Pipeline

## Overview

This repository contains a command-line interface (CLI) tool designed for generating and processing augmentations on video segments, specifically tailored for datasets like EPIC-Kitchens. The tool is structured to provide flexibility, robustness, and scalability, allowing for efficient handling of large datasets and complex augmentation strategies. The primary goal is to create high-quality training data for a video segment quality estimator, which is crucial for improving egocentric action recognition models.

## Table of Contents

- [Motivation](#motivation)
- [Pipeline Overview](#pipeline-overview)
- [Design Decisions](#design-decisions)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Generate Augmentation Plan](#1-generate-augmentation-plan)
  - [2. Process Augmentation Plan](#2-process-augmentation-plan)
- [Future Work](#future-work)
- [Contributing](#contributing)
- [License](#license)

## Motivation

### Why This Pipeline Exists

In the context of developing a video segment quality estimator for egocentric action recognition, it became essential to create a structured way to generate and manage augmentations of video segments from the EPIC-Kitchens dataset. These augmentations simulate various real-world data degradations, such as occlusions, variations in action completeness, and object presence challenges, which are critical for training models that can generalize well to real-world conditions.

The original dataset is organized by RGB frames stored in a structured directory format. The corresponding CSV file contains metadata about each video segment, including timestamps, frame numbers, action labels, and object classes. The goal of this pipeline is to:
1. **Generate Augmentations**: Create multiple augmented versions of each video segment, simulating different types of data degradations.
2. **Maintain Structure**: Ensure that the augmented data is saved in a consistent directory structure, with accompanying CSV files that retain essential metadata such as quality scores and original action labels.
3. **Support Quality Estimation**: The augmented dataset is intended to serve as training data for a video segment quality estimator, making it crucial to maintain high fidelity between the augmented data and the original annotations.

### Augmentation Strategy

In our pursuit of an effective training data estimator for egocentric action recognition, we recognize the multitude of potential degradations that can impact real-world data. These include not only the three key dimensions we've chosen to focus on—occlusion, action completeness, and object presence—but also visual challenges like motion blur, camera jitter, lighting variations, and viewpoint changes, as well as data-specific issues such as sensor noise and compression artifacts.

Given the complexity of these factors, our initial data generation process prioritizes the core three dimensions. By addressing these foundational challenges first, we establish a robust baseline for evaluating training data quality and lay the groundwork for future enhancements that encompass a broader spectrum of degradations.

## Pipeline Overview

### Two-Step Process

The pipeline is designed as a two-step process:

1. **Generate Augmentation Plan**: This step creates a detailed CSV file that outlines all the augmentations to be performed. The plan specifies which video segments will be augmented, the types of augmentations to apply, and any associated parameters. This allows for a review and potential modification of the plan before processing, ensuring that the augmentations align with the desired strategy.

2. **Process Augmentation Plan**: In this step, the pipeline reads the augmentation plan and executes the specified augmentations, saving the results to disk. The processing step is designed to be interruptible, with progress tracked in a separate CSV file, allowing the process to be paused and resumed as needed.

### Dataset Structure

The original dataset is organized with RGB frames stored in a directory structure based on participant and video IDs:

```sh
P01/P01_01/frame_0000000001.jpg
```

The dataset is accompanied by a CSV file with the following structure:

```csv
narration_id,participant_id,video_id,narration_timestamp,start_timestamp,stop_timestamp,start_frame,stop_frame,narration,verb,verb_class,noun,noun_class,all_nouns,all_noun_classes
P01_01_101,P01,P01_01,00:08:00.020,00:08:01.47,00:08:02.21,28888,28932,open cupboard,open,3,cupboard,3,['cupboard'],[3]
```

Augmented data is saved in a similar directory structure under a new root, with accompanying CSV files that maintain the necessary metadata.

## Design Decisions

### Modular CLI Structure

The CLI is designed to be modular, with each major task (plan generation, augmentation processing) implemented as a separate command. This structure allows for greater flexibility in managing the augmentation process, especially when working with large datasets that require careful planning and execution.

### Granular Progress Tracking

To handle large datasets and potentially long processing times, the pipeline includes:
- **Segment-Level Progress Tracking**: A progress bar tracks the completion of segments, providing high-level feedback on the overall process.
- **Frame-Level Progress Tracking**: Within each segment, a secondary progress bar tracks the processing of individual frames, offering granular insight into the augmentation process.

### Resumable Processing

The pipeline is designed to be interruptible. Progress is saved after each segment is processed, allowing the user to pause and resume the process without losing work. This is particularly important for large-scale data augmentation tasks that may need to be spread across multiple sessions.

### Customizable Augmentation Strategies

The pipeline allows for easy customization of augmentation strategies:
- **Flexible Augmentation Logic**: Different types of augmentations (e.g., occlusions, action completeness, object presence) can be applied with specific parameters.
- **Extensible Design**: The design allows for the addition of new augmentation types or modification of existing ones with minimal changes to the codebase.

## Features

- **CLI Tool**: Simple command-line interface for generating and processing augmentations.
- **Modular and Flexible**: Easily customize which segments to augment and what types of augmentations to apply.
- **Robust Progress Tracking**: Includes detailed progress tracking at both the segment and frame levels, with the ability to resume processing after interruptions.
- **Error Handling**: Captures and logs errors for each segment, ensuring that issues can be addressed without halting the entire process.

## Installation

To install the dependencies for this project, run:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Generate Augmentation Plan

The first step is to generate an augmentation plan based on your dataset. This plan outlines which segments will be augmented and how.

```bash
rm -rf ./out/generated; python augment-cli.py generate-plan --csv-path /home/ec2-user/environment/data-estimator/base_quality.csv --original-root ../ --plan-csv-path ./out/augmentation_plan.csv --augmented-segments-csv-path ./out/augmentated_segments.csv
```

- `--csv-path`: Path to the original CSV file containing video segment information.
- `--original-root`: Path to the root directory of the original video frames.
- `--plan-csv-path`: Path to save the generated augmentation plan CSV.

### 2. Process Augmentation Plan

Once the plan is generated, you can process the augmentations. This command applies the specified augmentations and saves the results, while also tracking progress.

```bash
rm ./out/progress.csv; python augment-cli.py process-plan --plan-csv-path ./out/augmentation_plan.csv --augmented-root ./out/generated --progress-csv-path ./out/progress.csv
```

- `--plan-csv-path`: Path to the augmentation plan CSV.
- `--augmented-root`: Root directory to save augmented frames.
- `--progress-csv-path`: Path to save the progress of augmentation processing.

## Future Work

The following enhancements are planned for future iterations of this tool:
- **Additional Augmentation Types**: Integration of more complex and varied augmentations (e.g., lighting changes, motion blur).
- **Parallel Processing**: Support for distributed or parallel processing to further speed up augmentation on large datasets.
- **Automated Quality Assessment**: Integration of automated quality assessment to evaluate the effectiveness of the generated augmentations in real-time.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or file an issue with suggestions or improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
