from collections import Counter
from typing import List, Dict

import pandas as pd
import torch
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from tqdm import tqdm


class GroupOfVectorsKNN:
    def __init__(self, distance_function=None):
        # self.model = neighbors.KNeighborsClassifier(metric="precomputed")
        # self.model = neighbors.KNeighborsClassifier(n_neighbors=1, algorithm='brute', metric=distance_function)
        # self.model = neighbors.KNeighborsClassifier(n_neighbors=1, metric=distance_function)

        self.X: [Dict, List] = None
        self.y: Dict = None
        self.minimal_number_of_vectors = 100
        self.distance_function = distance_function
        self.K = 5

    def fit(self, X: [dict, List], y: dict):
        self.X = self.filter_bad_groups_of_vectors(X)
        self.y = {k: v for k, v in y.items() if k in self.X}

    def filter_bad_groups_of_vectors(self, X):
        return {group_id: list_of_vectors for group_id, list_of_vectors in X.items() if
                len(list_of_vectors) >= self.minimal_number_of_vectors}

    def most_frequent(self, List):
        occurence_count = Counter(List)
        return occurence_count.most_common(1)[0][0]

    def predict(self, X):
        distances = []
        min_group_ids = []
        for query_group_id, query_vectors in tqdm(X.items()):
            curr_labels = []
            min_distances = []
            for cur_group_id, cur_vectors in self.X.items():
                d = self.distance_function(query_vectors, cur_vectors)
                if len(min_distances) < self.K or d < min_distances[0]:
                    min_distances.append(d)
                    min_distances = min_distances[-self.K:]
                    curr_labels.append(cur_group_id)
                    curr_labels = curr_labels[-self.K:]

            min_group_ids.append(self.most_frequent(curr_labels))
            distances.append(min_distances)

        labels = self.y[min_group_ids]

        return labels, distances, min_group_ids

    def score(self, X, y):
        pass


class ClusteringTfidfKNNClassifier(GroupOfVectorsKNN):

    def __init__(self):
        GroupOfVectorsKNN.__init__(self)
        self.clustering_model = None
        self.vectors_tokenizer = KNeighborsClassifier(n_neighbors=1)
        self._df_vectors_to_tokens = None
        self.groups_embedder = TfidfVectorizer(token_pattern=r"\d+")
        self.groups_embedding = None
        self.groups_classifier = KNeighborsClassifier(n_neighbors=3)

    def get_vectors_to_tokens(self):
        assert self.X is not None
        all_vectors, all_vectors_source_idx = self._unpack_X_to_ids_and_vectors(self.X)
        self.clustering_model.fit(torch.stack(all_vectors))

        return pd.DataFrame({"vectors": all_vectors,
                             "source_id": all_vectors_source_idx,
                             "tokens": [str(pred) for pred in self.clustering_model.labels_]})

    def _unpack_X_to_ids_and_vectors(self, X):
        all_vectors = []
        all_vectors_source_idx = []
        for X_id, vectors_list in X.items():
            for vec in vectors_list:
                all_vectors.append(vec)
                all_vectors_source_idx.append(X_id)
        return all_vectors, all_vectors_source_idx

    def fit(self, X: Dict[str, List], y: Dict):
        super(ClusteringTfidfKNNClassifier, self).fit(X, y)
        num_samples = sum([len(list_vecs) for list_vecs in self.X.values()])
        self.clustering_model = AgglomerativeClustering(n_clusters=num_samples // 4,
                                                        affinity="cosine",
                                                        linkage="average")
        self._df_vectors_to_tokens = self.get_vectors_to_tokens()
        self.vectors_tokenizer.fit(torch.stack(list(self._df_vectors_to_tokens["vectors"])),
                                   self._df_vectors_to_tokens["tokens"])

        corpus = self.generate_corpus_from_df(self._df_vectors_to_tokens)
        self.groups_embedding = self.groups_embedder.fit_transform(list(corpus))
        self.groups_classifier.fit(self.groups_embedding, list(self.y.values()))

    @staticmethod
    def generate_corpus_from_df(df) -> pd.Series:
        df["tokens"] = df["tokens"].apply(lambda x: x + " ")
        all_tokens_per_id = df[["source_id", "tokens"]].groupby("source_id").sum()["tokens"]
        return all_tokens_per_id

    def predict(self, X: Dict[str, List]):
        assert self._df_vectors_to_tokens is not None
        df_tokenized = self._tokenize_new_data_to_old_tokens(X)
        corpus_to_predict = self.generate_corpus_from_df(df_tokenized)
        target_embedding = self.groups_embedder.transform(corpus_to_predict)
        y_pred = self.groups_classifier.predict(target_embedding)
        return y_pred

    def _tokenize_new_data_to_old_tokens(self, X) -> pd.DataFrame:
        all_vectors, all_vectors_source_idx = self._unpack_X_to_ids_and_vectors(X)
        tokens = self.vectors_tokenizer.predict(torch.stack(all_vectors))
        return pd.DataFrame({"vectors": all_vectors,
                             "source_id": all_vectors_source_idx,
                             "tokens": tokens})
