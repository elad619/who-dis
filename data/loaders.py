import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import logging

logger = logging.getLogger()


def load_capas_from_jsons(json_dir:os.PathLike, label_extraction:str='dirname')->pd.DataFrame:
    dfs = []
    all_json_paths = list(Path(json_dir).rglob('*.json'))
    for capa_json_path in tqdm(all_json_paths, desc='Loading json files'):
        capa_df = pd.read_json(capa_json_path)
        if label_extraction=='dirname':
            capa_df['label'] = capa_json_path.parent.name
        else:
            raise NotImplementedError
        dfs.append(capa_df)
    logger.info("Finished Loading jsons, ")
    loaded=pd.concat(dfs)
    capas_df = loaded['capas'].apply(pd.Series)
    capas_df['uid'] = loaded['sha256']
    capas_df['label'] = loaded['label'].astype('string')
    capas_df['rule'] = capas_df['rule'].astype('string')
    return capas_df