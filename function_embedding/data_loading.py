from collections import defaultdict
from pathlib import Path
from typing import Tuple, Dict, List

import pandas as pd
import torch
from cachier import cachier
from tqdm import tqdm


def get_train_test_data(labels_dir: Path) -> Tuple[pd.Series, pd.Series]:
    train_data = pd.read_csv(Path(labels_dir, "train_samples.csv")).set_index("sample_name")
    test_data = pd.read_csv(Path(labels_dir, "test_samples.csv")).set_index("sample_name")
    return train_data["family"], test_data["family"]


@cachier()
def load_all_embeddings_from_dir(embeddings_dir_path: Path) -> Tuple[Dict[str, List], Dict[str, str]]:
    X = defaultdict(list)
    y = dict()

    for class_path in tqdm(embeddings_dir_path.glob("*")):
        for malware_file in class_path.glob("*"):
            malware_file_id = malware_file.name
            y[malware_file_id] = class_path.name
            for function_emb_path in malware_file.glob("*.pt"):
                X[malware_file_id].append(torch.load(function_emb_path))
    return X, y


def get_embeddings_dataset(labels_dir: Path, embeddings_dir_path: Path, clear_cache: bool = False):
    if clear_cache:
        load_all_embeddings_from_dir.clear_cache()
    X_from_embedding_dir, y_from_embedding_dir = load_all_embeddings_from_dir(embeddings_dir_path)
    y_train, y_test = get_train_test_data(labels_dir)
    X_train, X_test = {}, {}

    for malware_id, family in y_train.items():
        try:
            family_from_embedding_dir = y_from_embedding_dir[f"function_embeddings-{malware_id}"]
            assert y_from_embedding_dir[f"function_embeddings-{malware_id}"] == family, \
                f"id: {malware_id} is bad, in gt: {family}, in embedding: {family_from_embedding_dir}"
            X_train[malware_id] = X_from_embedding_dir[f"function_embeddings-{malware_id}"]
        except KeyError:
            pass
    for malware_id, family in y_test.items():
        try:
            family_from_embedding_dir = y_from_embedding_dir[f"function_embeddings-{malware_id}"]
            assert family_from_embedding_dir == family, \
                f"id: {malware_id} is bad, in gt: {family}, in embedding: {family_from_embedding_dir}"
            X_test[malware_id] = X_from_embedding_dir[f"function_embeddings-{malware_id}"]
        except KeyError:
            pass

    y_train = y_train[X_train.keys()]
    y_test = y_test[X_test.keys()]
    return X_train, X_test, y_train, y_test


if __name__ == '__main__':
    # load_all_embeddings_from_dir.clear_cache()
    all_data_dir = Path(Path(r"C:\Users\yaara\OneDrive\Desktop\who_dis_data_test"))
    embeddings_dir = Path(all_data_dir, "embeddings")
    labels_dir = Path(all_data_dir, "train_test_split")
    X_train, X_test, y_train, y_test = get_embeddings_dataset(labels_dir, embeddings_dir, clear_cache=True)
import plotly.express as px
px.histogram()