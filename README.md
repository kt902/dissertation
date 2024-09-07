# Video Quality Estimation and Action Recognition

This repository contains the code and resources for the video quality estimation and action recognition project. The project explores how video quality affects the performance of action recognition models using Temporal Segment Networks (TSN) and AVION architectures. It also includes tools for dataset annotation, augmentation, and model training for both action recognition and video quality estimation tasks.

## Project Structure

- **annotation-ui**: Contains the web-based user interface for manual annotation of video segments. 
- **augmentation-pipeline**: A pipeline for augmenting video datasets with different types of quality degradations, used to train models with varied data. Scripts include CLI tools to manage the augmentation process.
- **research**: Contains subfolders for action recognition models (TSN, AVION), datasets, training logs, and results. Each subfolder includes necessary resources for model implementation and testing.
    - **AVION** (git submodule): Contains the AVION model with custom modifications to work with our quality estimator project.
    - **C1-Action-Recognition-TSN-TRN-TSM** (git submodule): Contains the TSN, TRN, and TSM models with necessary changes to support video quality estimation.
    - **data**: Contains the datasets used for both action recognition and quality estimation. These include the EPIC-KITCHENS dataset splits and manually annotated quality datasets.
    - **data-estimator**: Files related to the quality estimator including training, validation, and test sets, along with model results.
    - **estimator-figures**: Visualizations and statistics from the quality estimation results (e.g., MAE plots, class-based MAE statistics).
    - **figures**: Correlation heatmaps, quality score distributions, and other plots used in analysis.
    - **scripts**: Utility scripts for video preprocessing, downloading, resizing, and dataset management.
    - **scripts-estimator**: Scripts related to dataset preparation and evaluation for the quality estimator.

## Initializing Submodules

The **AVION** and **C1-Action-Recognition-TSN-TRN-TSM** directories are git submodules. These contain crucial modifications necessary for adapting these models to work within the scope of this project. To initialize and update the submodules after cloning the repository, run the following commands:

```bash
git clone https://github.com/kt902/dissertation.git
cd dissertation
git submodule init
git submodule update
```

This will pull in the required submodules with the custom changes that allow AVION and TSN to work with the video quality estimation task.

## Key Components

1. **Action Recognition**: 
   - We evaluate both **Temporal Segment Networks (TSN)** and **AVION**, comparing their performance on the EPIC-KITCHENS dataset. Both models are finetuned with a regression head for video quality estimation. 
   - The **C1-Action-Recognition-TSN-TRN-TSM** submodule contains the code for TSN, TRN, and TSM architectures, including modifications that enable them to handle our quality estimation task.
   - The **AVION** submodule contains the AVION architecture with adjustments for working with video quality estimation and regression-based learning.

2. **Data Augmentation**:
   - A custom pipeline for generating augmented versions of the dataset with varied quality degradations. The `augmentation-pipeline` folder includes tools for creating and managing these augmentations.

3. **Quality Estimation**:
   - A custom quality estimation model, built on top of TSN and AVION, is trained to predict video quality scores using a regression head.
   - Augmented datasets are used to improve generalization, and different metrics (e.g., MAE) are used to evaluate performance. 
   - Scripts in `scripts-estimator` are used to evaluate quality metrics, generate correlation plots, and assess performance across various subgroups.

## Running the Annotation UI
```bash
cd annotation-ui
npm run dev
```
The UI allows you to annotate video segments, which is key for building quality datasets.

### Training Models
For training the action recognition or quality estimation models, refer to the configuration files in `research/AVION` and `research/C1-Action-Recognition-TSN-TRN-TSM`.

## Future Work

- **Progressive Unfreezing**: Investigating a more gradual unfreezing of layers in the model during fine-tuning.
- **Hyperparameter Tuning**: Testing different optimizer settings, learning rates, and loss functions.
- **Dataset Expansion**: Using larger and more varied datasets to improve model generalization.
- **Classification Loss**: Exploring classification loss as an alternative to regression to improve model performance on smaller datasets.
