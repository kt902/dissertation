import os
import pandas as pd
import requests
import io
import concurrent.futures
import multiprocessing

class EpicURLBuilder:
    def __init__(self,
                 epic_55_base_url='https://data.bris.ac.uk/datasets/3h91syskeag572hl6tvuovwv4d',
                 epic_100_base_url='https://data.bris.ac.uk/datasets/2g1n6qdydwa9u22shpxqzp0t8m',
                 epic_55_splits=None):
        self.base_url_55 = epic_55_base_url.rstrip('/')
        self.base_url_100 = epic_100_base_url.rstrip('/')
        self.splits = self.load_splits(epic_55_splits) if epic_55_splits else {}

    def load_splits(self, splits_source):
        if splits_source.startswith('http://') or splits_source.startswith('https://'):
            response = requests.get(splits_source)
            splits_df = pd.read_csv(io.StringIO(response.text))
        else:
            splits_df = pd.read_csv(splits_source)

        splits_dict = {}
        for _, row in splits_df.iterrows():
            splits_dict[row['video_id']] = row['split']
        return splits_dict

    def get_video_url(self, video_id, file_ext='MP4'):
        parts = video_id.split('_')
        participant = parts[0]
        is_extension = len(parts[1]) == 3  # Detect if it's an EPIC 100 extension video (e.g., P01_001)

        if is_extension:
            # EPIC 100 video
            url = f"{self.base_url_100}/{participant}/videos/{video_id}.{file_ext}"
        else:
            # EPIC 55 video
            split = self.splits.get(video_id, 'train')  # Default to 'train' if split is not found
            url = f"{self.base_url_55}/videos/{split}/{participant}/{video_id}.{file_ext}"

        return url
