Run a Docker container with aria2 for downloading Academic Torrents

```
docker run --rm -it -v $PWD:$PWD -w $PWD --entrypoint=/bin/bash p3terx/aria2-pro 
```

Parallel downloads:
```sh
# For example you can get all the VISOR annotation URLs into
# txt.

aria2c -i urls.txt -d ./my_downloads --continue=true --max-concurrent-downloads=8 --summary-interval=5
```

Get academic torrents links from https://epic-kitchens.github.io/2024#downloads
```sh
# Extended
wget https://academictorrents.com/download/c92b4a3cd3834e9af9666ac82379ff15ca289a83.torrent
# Original
wget https://academictorrents.com/download/d08f4591d1865bbe3436d1eb25ed55aae8b8f043.torrent
```

Get CSV with EPIC-55 splits
```sh
mkdir -p data
wget https://raw.githubusercontent.com/epic-kitchens/epic-kitchens-download-scripts/master/data/epic_55_splits.csv -O ./data/epic_55_splits.csv
```

Setup Conda on AWS
```sh
wget https://repo.anaconda.com/archive/Anaconda3-2024.06-1-Linux-x86_64.sh
bash Anaconda3-2024.06-1-Linux-x86_64.sh 
eval "$(/home/ec2-user/anaconda3/bin/conda shell.zsh hook)"
conda init zsh
cd C1-Action-Recognition-TSN-TRN-TSM/
conda env create -n epic-models -f environment.yml
conda activate epic-models
```

Gulp
```sh
cd ~/environment/torrents/epic-torrents-1/2g1n6qdydwa9u22shpxqzp0t8m/P01/rgb_frames
tar -xvf P01_101.tar --one-top-level
rm -rf ./P01_101_gulp; python ./src/gulp_data.py ./ ./P01_101_gulp ./labels.csv rgb

python ./src/test.py --batch-size=32 --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results/results.pt


python ./src/test.py --batch-size=32 --split test --datadir ./P01_101_gulp ./models/tsn_rgb.ckpt ./results/results.pt

# See configs/tsn_rgb.yaml for an example configuration file.
# You can overwrite config files by passing key-value pairs as arguments
# You can change the config by setting --config-name to the name of a file in configs
# without the yaml suffix.
# $ python src/train.py \
#     --config-name tsn_rgb \
#     data._root_gulp_dir=/path/to/gulp/root \
#     data.worker_count=$(nproc) \
#     learning.batch_size=64 \
#     trainer.gpus=4 \
#     hydra.run.dir=outputs/experiment-name
# $ python src/finetune.py \
#     --config-name tsn_rgb \
#     data._root_gulp_dir=/path/to/gulp/root \
#     data.worker_count=$(nproc) \
#     learning.batch_size=32 \
#     trainer.gpus=1 \
#     hydra.run.dir=outputs/experiment-name

$ python ./add_negative_examples_to_dataset.py
$ rm -rf ./gulped/rgb_validation; python ./src/gulp_data.py ./ ./gulped/rgb_validation /home/ec2-user/environment/data-estimator/base_val.csv rgb
$ rm -rf ./gulped/rgb_test; python ./src/gulp_data.py ./ ./gulped/rgb_test /home/ec2-user/environment/data-estimator/base_test.csv rgb
$ rm -rf ./gulped/rgb_train; python ./src/gulp_data.py ./ ./gulped/rgb_train ./train.csv rgb

# $ python ./src/finetune.py --batch-size=128 ./models/tsn_rgb.ckpt ./results/results.pt
$ nvidia-smi -l
# View logs with tensorboard
$ tensorboard --logdir ./lightning_logs --bind_all
$ tensorboard --logdir outputs/experiment-name --bind_all

# $ python ./src/test.py --batch-size=32 --split test ./lightning_logs/version_${version}/checkpoints/epoch*.ckpt ./results/results.pt
# $ python ./src/test.py --batch-size=32 --split test ./lightning_logs/version_${version}/checkpoints/last.ckpt ./results/results.pt

# python ./src/test.py --batch-size=16 --split test ./lightning_logs/version_63/checkpoints/last.ckpt ./results/results.pt


```

Results :'(
```shell
(epic-models) ➜  C1-Action-Recognition-TSN-TRN-TSM git:(dissertation) ✗ python ./peek.py
Columns in quality_data: Index(['user_id', 'narration_id', 'participant_id', 'video_id',
       'action_presence', 'camera_motion', 'lighting', 'focus',
       'action_completeness', 'object_presence'],
      dtype='object')
Mean Absolute Error (MAE): 0.1040
Mean Squared Error (MSE): 0.0339
Root Mean Squared Error (RMSE): 0.1842
R-squared (R²): -0.1514
```

Recursively fix the ownership of the torrent directories
```sh
chown -R [user]:[group] [directory].
```

Sort out SSH key permissions
```sh
chmod 600 ~/.ssh/id_rsa 
ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub
```
----

# AVION

Create environment
```sh
conda config --append channels conda-forge
conda create --name avion python=3.10 -y
conda activate avion
pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117
pip install ninja==1.11.1  # install ninja first for building flash-attention
CUDA_HOME=$CUDA_HOME pip install -r requirements.txt


wget https://developer.download.nvidia.com/compute/cuda/11.7.0/local_installers/cuda_11.7.0_515.43.04_linux.run
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/install-nvidia-driver.html#gpu-instance-install-cuda

export CUDA_HOME=/usr/local/cuda
```


```sh

git submodule update --init --recursive
cd third_party/decord/
mkdir build && cd build
cmake .. -DUSE_CUDA=0 -DCMAKE_BUILD_TYPE=Release -DFFMPEG_DIR=$HOME/ffmpeg_build
make

cd ../python
python setup.py install --user

export LD_LIBRARY_PATH=$HOME/ffmpeg_build/lib/:$LD_LIBRARY_PATH
python -c "import decord; print(decord.__path__)"
```


```sh
# https://www.maskaravivek.com/post/how-to-install-ffmpeg-on-ec2-running-amazon-linux/
sudo su -
cd /usr/local/bin
mkdir ffmpeg && cd ffmpeg
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz
cp -a /usr/local/bin/ffmpeg/ffmpeg-*-static/* /usr/local/bin/ffmpeg/
ln -s /usr/local/bin/ffmpeg/ffmpeg /usr/bin/ffmpeg

wget https://www.ffmpeg.org/releases/ffmpeg-7.0.2.tar.xz
tar -xf ffmpeg-7.0.2.tar.xz
```

```sh
mkdir $EXP_PATH
# torchrun --nproc_per_node=8 

LD_LIBRARY_PATH=$HOME/ffmpeg_build/lib/:$LD_LIBRARY_PATH \
PYTHONPATH=/home/ec2-user/environment/AVION:/home/ec2-user/environment/AVION/third_party/decord/python \
torchrun --nproc_per_node=1 \
    scripts/main_lavila_finetune_cls.py \
    --root datasets/EK100/EK100_320p_15sec_30fps_libx264/ \
    --video-chunk-length 15 --use-flash-attn \
    --grad-checkpointing \
    --use-fast-conv1 \
    --gpu 0 \
    --workers 2 \
    --batch-size 16 \
    --pickle-filename results.pt \
    --fused-decode-crop \
    --pretrain-model scripts/avion_pretrain_lavila_vitl_best.pt \
    --resume scripts/avion_finetune_cls_lavila_vitl_best.pt \
    --evaluate 
```


Modify VS Code settings
```
@id:python.analysis.exclude 
```

---

Evaluate my quality dataset against the model...

TSN
```sh
rm -rf ./gulped/rgb_quality; python ./src/gulp_data.py ./ ./gulped/rgb_quality /home/ec2-user/environment/data-estimator/base_quality.csv rgb
python ./src/test.py --gpus 4 --batch-size=32 --datadir ./gulped/rgb_quality --split test ./models/tsn_rgb.ckpt ./results/quality-results.pt



rm -rf ./gulped/rgb_quality_all; python ./src/gulp_data.py ./ ./gulped/rgb_quality_all ./example.csv rgb
rm -rf ./gulped/rgb_quality_all; python ./src/gulp_data.py ./ ./gulped/rgb_quality_all /home/ec2-user/environment/my-dissertation/augmentation-pipeline/out/augmentated_segments.csv rgb
python ./src/test.py --gpus 4 --batch-size=32 --datadir ./gulped/rgb_quality_all --split test ./models/tsn_rgb.ckpt ./results/quality_all_results.pt
```

AVION
```sh
LD_LIBRARY_PATH=$HOME/ffmpeg_build/lib/:$LD_LIBRARY_PATH \
PYTHONPATH=/home/ec2-user/environment/AVION:/home/ec2-user/environment/AVION/third_party/decord/python \
torchrun --nproc_per_node=4 \
    scripts/main_lavila_finetune_cls.py \
    --root datasets/EK100/EK100_320p_15sec_30fps_libx264/ \
    --val-metadata /home/ec2-user/environment/data-estimator/base_quality.csv \
    --video-chunk-length 15 --use-flash-attn \
    --grad-checkpointing \
    --use-fast-conv1 \
    --gpu 0 \
    --workers 2 \
    --batch-size 16 \
    --pickle-filename results/quality_results.pt \
    --fused-decode-crop \
    --pretrain-model scripts/avion_pretrain_lavila_vitl_best.pt \
    --resume scripts/avion_finetune_cls_lavila_vitl_best.pt \
    --evaluate 

LD_LIBRARY_PATH=$HOME/ffmpeg_build/lib/:$LD_LIBRARY_PATH \
PYTHONPATH=/home/ec2-user/environment/AVION:/home/ec2-user/environment/AVION/third_party/decord/python \
torchrun --nproc_per_node=4 \
    scripts/main_lavila_finetune_cls.py \
    --root datasets/EK100/EK100_320p_15sec_30fps_libx264/ \
    --val-metadata /home/ec2-user/environment/my-dissertation/augmentation-pipeline/out/augmentated_segments.csv \
    --video-chunk-length 15 --use-flash-attn \
    --grad-checkpointing \
    --use-fast-conv1 \
    --gpu 0 \
    --workers 2 \
    --batch-size 16 \
    --pickle-filename results/quality_all_results.pt \
    --fused-decode-crop \
    --pretrain-model scripts/avion_pretrain_lavila_vitl_best.pt \
    --resume scripts/avion_finetune_cls_lavila_vitl_best.pt \
    --evaluate 
```

Interesting file:

/home/ec2-user/anaconda3/envs/epic-models/lib/python3.8/site-packages/gulpio2/fileio.py