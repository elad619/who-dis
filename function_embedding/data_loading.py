from pathlib import Path
from typing import Tuple, Dict, List
from collections import defaultdict

import pandas as pd
import torch


def get_train_test_data(labels_dir: Path) -> Tuple[pd.Series, pd.Series]:
    train_data = pd.read_csv(Path(labels_dir, "train_samples.csv")).set_index("sample_name")
    test_data = pd.read_csv(Path(labels_dir, "test_samples.csv")).set_index("sample_name")
    return train_data["family"], test_data["family"]


def load_all_embeddings_from_dir(embeddings_dir_path: Path) -> Tuple[Dict[str, List], Dict[str, str]]:
    classes = ["Orcus", "Conti", "SugarRandsomware", "Emotet", "7ev3n"]
    X = defaultdict(list)
    y = dict()

    for c in classes:
        class_embedding_path = Path(embeddings_dir_path, c)
        for malware_file in class_embedding_path.glob("*"):
            malware_file_id = malware_file.name
            y[malware_file_id] = c
            for function_emb_path in malware_file.glob("*.pt"):
                X[malware_file_id].append(torch.load(function_emb_path))
    return X, y


def get_embeddings_dataset(labels_dir: Path, embeddings_dir_path: Path):
    X_from_embedding_dir, y_from_embedding_dir = load_all_embeddings_from_dir(embeddings_dir_path)
    y_train, y_test = get_train_test_data(labels_dir)
    X_train, X_test = [], []

    for malware_id, family in y_train.items():
        assert y_from_embedding_dir[malware_id] == family
        X_train.append(X_from_embedding_dir[malware_id])
    for malware_id, family in y_test.items():
        assert y_from_embedding_dir[malware_id] == family
        X_test.append(X_from_embedding_dir[malware_id])


if __name__ == '__main__':
    all_data_dir = Path(___)
    embeddings_dir = Path(all_data_dir, "embeddings")
    labels_dir = Path(all_data_dir, "train_test_split")
