from collections import defaultdict
import os
from typing import Dict, Sequence, Tuple
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import logging
import json
import numpy as np

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
    post_fix=''
    if ver=='wipbot':
        split_names = [f"wipbot_samples.csv"]
    elif ver=='v3':
        post_fix=f'_{ver}'
        split_names = [f"train_samples{post_fix}.csv", f"test_samples{post_fix}.csv",f"hard_samples{post_fix}.csv"]
    elif 'v' in ver:
        post_fix=f'_{ver}'
        split_names = [f"train_samples{post_fix}.csv", f"test_samples{post_fix}.csv"]
    
    split_data = []
    for split_name in split_names:
        split_data.append(pd.read_csv(Path(labels_dir, split_name)).set_index("sample_name")["family"])
    return split_data

def extract_capa_for_model(cats_df:pd.DataFrame, column:str)->pd.DataFrame:
    cats_df['dummy'] = 1
    features_df = pd.pivot_table(cats_df, values='dummy', index=['uid'], columns=[column], aggfunc=np.sum, fill_value=0)
    features_df = (features_df>=1).astype(int)
    features_df['label'] = cats_df.groupby('uid')['label'].first()
    return features_df

def load_split(train_test_split_dir:os.PathLike, features_df:pd.DataFrame, split_ver:str)->Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if split_ver=='v3':
        train_split, test_split, hard_test_split = get_train_test_data(train_test_split_dir, ver=split_ver)
        train_index  = np.intersect1d(train_split.index, features_df.index)
        test_index  = np.intersect1d(test_split.index, features_df.index)
        hard_test_index  = np.intersect1d(hard_test_split.index, features_df.index)
        features_train = features_df.loc[train_index]
        features_test = features_df.loc[test_index]
        hard_features_test = features_df.loc[hard_test_index]
    else:
        train_split, test_split = get_train_test_data(train_test_split_dir, ver=split_ver)
        train_index  = np.intersect1d(train_split.index, features_df.index)
        test_index  = np.intersect1d(test_split.index, features_df.index)
        features_train = features_df.loc[train_index]
        features_test = features_df.loc[test_index]
        hard_features_test = pd.DataFrame(columns=features_df.columns)
    return features_train, features_test, hard_features_test


if __name__=="__main__":
    capas_dir = r'C:\Users\stav\data\whodis\parsed\CAPAs'
    dfs = load_capas_from_jsons(capas_dir)