from typing import List

from sklearn import neighbors


class GroupOfVectorsNearestNeighbors:
    def __init__(self, victors_group_distance="naive"):
        self.model = neighbors.KNeighborsClassifier(metric="precomputed")
        self.X: [dict, List] = None
        self.y: dict = None
        self.vector_similatiry = "cosine"
        self.minimal_number_of_vectors = 100
        self.victors_group_distance = victors_group_distance

    @staticmethod
    def distance_naive(group_of_vectors_1: List, group_of_vectors_2: List):
        if len(group_of_vectors_1) <= len(group_of_vectors_2):
            query_group = group_of_vectors_1
            other_group = group_of_vectors_2
        else:
            query_group = group_of_vectors_2
            other_group = group_of_vectors_1

        distance_matrix = compute_distance_matrix(query_group, other_group)
        per_function_min = distance_matrix.min(axis=1)
        distance = sum_squer(per_function_min)
        return distance

    def fit(self, X: [dict, List], y: dict):
        self.X = self.filter_bad_groups_of_vectors(X)
        self.y = y

    def filter_bad_groups_of_vectors(self, X):
        return {group_id: list_of_vectors for group_id, list_of_vectors in X.items() if
                len(list_of_vectors) >= self.minimal_number_of_vectors}

    def predict(self, X):
        distances = []
        for query_group_id, query_vectors in X.items():
            for cur_group_id, cur_vectors in self.X.items():
                pass


