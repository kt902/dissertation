# How to get around

- [General notes for running things](../notes/RUN_EXPERIMENTS.md)
- [Pseudo-label generation work](../my-dissertation/augmentation-pipeline/main.py)
- [Script for clipping videos](../scripts/download_and_clip_videos.py)

- [Merge the UI annotations with the source of truth](../scripts-estimator/dataset_flattened_from_manual_annotations.py). No duplicates


```sh
# Merge the UI annotations with the source of truth
python ./scripts-estimator/dataset_flattened_from_manual_annotations.py
# Add  model results
python ./scripts-estimator/make_models_results_dataset_with_top_k.py --augment
python ./scripts-estimator/make_models_results_dataset_with_logits.py --augment
# Plot correlation plots
python ./scripts-estimator/plot_correlation_with_top_k.py
python ./scripts-estimator/plot_correlation_with_logits.py
python ./scripts-estimator/plot_dataset_statistics.py 
```


```sh
# Split the dataset
python ./scripts-estimator/split_dataset.py --augment
# TSN
cd C1-Action-Recognition-TSN-TRN-TSM/
rm -rf ./gulped/rgb_train_all; python ./src/gulp_data.py ./ ./gulped/rgb_train_all /home/ec2-user/environment/data-estimator/base_all_train.csv rgb
rm -rf ./gulped/rgb_validation_all; python ./src/gulp_data.py ./ ./gulped/rgb_validation_all /home/ec2-user/environment/data-estimator/base_all_val.csv rgb
rm -rf ./gulped/rgb_test_all; python ./src/gulp_data.py ./ ./gulped/rgb_test_all /home/ec2-user/environment/data-estimator/base_all_test.csv rgb

## Train
python ./src/finetune.py \
 --gpus=4 --batch-size=256 \
 --train-datadir=./gulped/rgb_train \
 --val-datadir=./gulped/rgb_validation \
./models/tsn_rgb.ckpt ./results/dummy.pt

python ./src/finetune.py \
 --gpus=4 --batch-size=256 \
 --train-datadir=./gulped/rgb_train_all \
 --val-datadir=./gulped/rgb_validation_all \
./models/tsn_rgb.ckpt ./results/dummy.pt

## Seperate terminal
nvidia-smi -l

## Test
python ./src/test.py --gpus 4 --batch-size=32 --datadir ./gulped/rgb_test_all --split test ./lightning_logs/version_85/checkpoints/last.ckpt ./results/finetune_results.pt
```