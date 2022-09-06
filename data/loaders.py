from collections import defaultdict
import os
from typing import Dict, Tuple
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import logging
import json

logger = logging.getLogger()


def load_capas_from_jsons(json_dir:os.PathLike, label_extraction:str='dirname')->Dict[str, pd.DataFrame]:
    
    def _read_sub_category(content:str, sub_cat:str, label:str):
        sub_cat_df =pd.DataFrame().from_records(content[sub_cat])
        file_sha =content['sha256']
        sub_cat_df['uid'] = file_sha
        sub_cat_df['label'] = label
        return sub_cat_df

    dfs = defaultdict(list)
    all_json_paths = list(Path(json_dir).rglob('*.json'))
    for capa_json_path in tqdm(all_json_paths, desc='Loading json files'):
        with open(capa_json_path, 'r') as json_file:
            content = json.loads(json_file.read())
        if label_extraction=='dirname':
            label = capa_json_path.parent.name
        else:
            raise NotImplementedError
        dfs['capas'].append(_read_sub_category(content,'capas',label))
        dfs['mbc'].append(_read_sub_category(content,'mbc',label))
    for sub_cat in dfs:
        dfs[sub_cat] = pd.concat(dfs[sub_cat])
    logger.info("Finished Loading jsons, ")
    return dict(dfs)


def get_train_test_data(labels_dir: Path, ver:str = 'v1') -> Tuple[pd.Series, pd.Series]:
    post_fix = '' if ver=='v1' else '_v2'
    train_data = pd.read_csv(Path(labels_dir, f"train_samples{post_fix}.csv")).set_index("sample_name")
    test_data = pd.read_csv(Path(labels_dir, f"test_samples{post_fix}.csv")).set_index("sample_name")
    return train_data["family"], test_data["family"]


if __name__=="__main__":
    capas_dir = r'C:\Users\stav\data\whodis\parsed\CAPAs'
    dfs = load_capas_from_jsons(capas_dir)