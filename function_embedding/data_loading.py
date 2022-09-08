
from pathlib import Path
from typing import Tuple, Dict, List

import pandas as pd
import torch
from tqdm.contrib.concurrent import thread_map


def get_train_test_data(labels_dir: Path, version=None) -> Tuple[pd.Series, pd.Series]:
    train_csv_name = "train_samples.csv" if version is None else f"train_samples_v{version}.csv"
    test_csv_name = "test_samples.csv" if version is None else f"test_samples_v{version}.csv"
    train_data = pd.read_csv(Path(labels_dir, train_csv_name)).set_index("sample_name")
    test_data = pd.read_csv(Path(labels_dir, test_csv_name)).set_index("sample_name")
    return train_data["family"], test_data["family"]


# @cachier()
def load_all_embeddings_from_dir(embeddings_dir_path: Path, load_only_file_named=None) -> Tuple[
    Dict[str, List], Dict[str, str]]:
    y = dict()

    all_malware_paths = []
    for class_path in embeddings_dir_path.glob("*"):
        for malware_file in class_path.glob("*"):
            malware_file_id = malware_file.name
            if load_only_file_named is None or \
                    malware_file_id.replace("function_embeddings-", "") in load_only_file_named:
                all_malware_paths.append(malware_file)
                y[malware_file_id] = class_path.name

    all_ids_and_vecs = thread_map(_load_all_vectors_from_dir, all_malware_paths,
                                  desc="loading vecs from files",
                                  max_workers=20,
                                  unit="malware")
    X = {malware_id: vecs_list for malware_id, vecs_list in all_ids_and_vecs}
    return X, y


def _load_all_vectors_from_dir(malware_file: Path) -> Tuple[str, List]:
    all_vecs = []
    malware_id = malware_file.name
    for function_emb_path in malware_file.glob("*.pt"):
        vec = torch.load(function_emb_path)
        if vec.abs().sum().bool():
            all_vecs.append(vec)
    return malware_id, all_vecs


def get_embeddings_dataset(labels_dir: Path, embeddings_dir_path: Path,
                           # clear_cache: bool = False,
                           dataset_version=None):
    # if clear_cache:
    #     load_all_embeddings_from_dir.clear_cache()
    y_train, y_test = get_train_test_data(labels_dir, dataset_version)
    all_malware_ids = list(y_train.index) + list(y_test.index)
    X_from_embedding_dir, y_from_embedding_dir = load_all_embeddings_from_dir(embeddings_dir_path, all_malware_ids)
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
    all_data_dir_path = Path(r"C:\Users\yaara\OneDrive\Desktop\who_dis_data")
    embeddings_dir = Path(all_data_dir_path, "embeddings")
    labels_dir = Path(all_data_dir_path, "train_test_split")

    X_train, X_test, y_train, y_test = get_embeddings_dataset(labels_dir, embeddings_dir, dataset_version=3)

    y_test = y_test[y_test.apply(lambda x: x in set(y_train))]
    X_test = {k: v for k, v in X_test.items() if k in list(y_test.index)}

    from nearest_neighbor import ClusteringTfidfKNNClassifier

    model = ClusteringTfidfKNNClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    from sklearn.metrics import accuracy_score, confusion_matrix
    print(accuracy_score(y_test, y_pred))
    print(confusion_matrix(y_test, y_pred))
