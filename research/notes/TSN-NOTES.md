
Setup Docker container to work from.
```sh
$ docker run --name dev -it -p 8888:8888 -v $PWD:$PWD -w $PWD --shm-size=1g --platform linux/amd64 continuumio/anaconda3 /bin/bash
$ apt-get update && apt-get install -y build-essential libgl1-mesa-glx
```

## Download dataset

```sh
cd epic-kitchens-download-scripts/
python epic_downloader.py --rgb-frames --participants P01
```

Test models:
```sh
apt-get update && apt-get install -y build-essential
conda env create -n epic-models -f environment.yml
conda activate epic-models
rm -rf ./P01_101_gulp; python ./src/gulp_data.py ./ ./P01_101_gulp ./labels.csv rgb
python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
```

Evaluate models
```sh
(epic-models) $ python evaluate.py     ../results.pt     ../labels.csv     --tail-verb-classes-csv ../epic-kitchens-100-annotations/EPIC_100_tail_verbs.csv     --tail-noun-classes-csv ../epic-kitchens-100-annotations/EPIC_100_tail_nouns.csv     --unseen-participant-ids ../epic-kitchens-100-annotations/EPIC_100_unseen_participant_ids_test.csv
all_action_accuracy_at_1: 55.55555555555556
all_action_accuracy_at_5: 83.33333333333334
all_noun_accuracy_at_1: 61.111111111111114
all_noun_accuracy_at_5: 94.44444444444444
all_verb_accuracy_at_1: 83.33333333333334
all_verb_accuracy_at_5: 100.0
tail_action_accuracy_at_1: 0.0
tail_noun_accuracy_at_1: 0.0
```
## Environment setup

We provide a conda environment definition in [`environment.yml`](./environment.yml
) that defines the dependencies you need to run this codebase. Simply set up the
 environment by running

```bash
$ conda env create -n epic-models -f environment.yml
$ conda activate epic-models
```

```sh
$ rm -rf ./P01_101_gulp; python ./src/gulp_data.py ./ ./P01_101_gulp ./labels.csv rgb
$ python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
$ python src/fuse.py ./results.pt ./results-fused.pt
$ python evaluate.py \
    ../results.pt \
    ../labels.csv \
    --tail-verb-classes-csv ../epic-kitchens-100-annotations/EPIC_100_tail_verbs.csv \
    --tail-noun-classes-csv ../epic-kitchens-100-annotations/EPIC_100_tail_nouns.csv \
    --unseen-participant-ids ../epic-kitchens-100-annotations/EPIC_100_unseen_participant_ids_test.csv

```

## Prep data

Gulp the train/validation/test sets from the provided extracted frames

### RGB
```bash
$ python src/gulp_data.py \
    /path/to/rgb/frames \
    gulp/rgb_train \
    /path/to/EPIC_100_train.pkl \
    rgb
$ python src/gulp_data.py \
    /path/to/rgb/frames \
    gulp/rgb_validation \
    /path/to/EPIC_100_validation.pkl \
    rgb
$ python src/gulp_data.py \
    /path/to/rgb/frames \
    gulp/rgb_test \
    /path/to/EPIC_100_test_timestamps.pkl
    rgb
```


---


```bash
# See configs/tsn_rgb.yaml for an example configuration file.
# You can overwrite config files by passing key-value pairs as arguments
# You can change the config by setting --config-name to the name of a file in configs
# without the yaml suffix.
$ python src/train.py \
    --config-name tsn_rgb \
    data._root_gulp_dir=/path/to/gulp/root \
    data.worker_count=$(nproc) \
    learning.batch_size=64 \
    trainer.gpus=4 \
    hydra.run.dir=outputs/experiment-name

# View logs with tensorboard
$ tensorboard --logdir outputs/experiment-name --bind_all
```



---

## Play locally
```
docker run --rm -v $PWD:$PWD -w $PWD -it --platform linux/amd64 python bash

20  pip install opencv-python
22  apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
```

```sh
(epic-models) root@9ecc3fd0c4c3:/Users/m1/Desktop/C1-Action-Recognition-TSN-TRN-TSM# history
    1  apt-get update && apt-get install -y build-essential
    2  conda env create -n epic-models -f environment.yml
    3  conda activate epic-models
    4  rm -rf ./P01_101_gulp; python ./src/gulp_data.py ./ ./P01_101_gulp ./labels.csv rgb
    5  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
    6  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
    7  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
    8  history
    9  clear
   10  python evaluate.py     ../results.pt     ../labels.csv     --tail-verb-classes-csv ../epic-kitchens-100-annotations/EPIC_100_tail_verbs.csv     --tail-noun-classes-csv ../epic-kitchens-100-annotations/EPIC_100_tail_nouns.csv     --unseen-participant-ids ../epic-kitchens-100-annotations/EPIC_100_unseen_participant_ids_test.csv
   11  cd C1-Action-Recognition/
   12  python evaluate.py     ../results.pt     ../labels.csv     --tail-verb-classes-csv ../epic-kitchens-100-annotations/EPIC_100_tail_verbs.csv     --tail-noun-classes-csv ../epic-kitchens-100-annotations/EPIC_100_tail_nouns.csv     --unseen-participant-ids ../epic-kitchens-100-annotations/EPIC_100_unseen_participant_ids_test.csv
   13  cd ..
   14  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
   15  pip3 install numpy==1.23.5
   16  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
   17  clear
   18  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
   19  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
   20  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
   21  git status
   22  git diff
   23  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
   24  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
   25  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
   26  python ./src/test.py --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results.pt
   27  history
(epic-models) root@9ecc3fd
```