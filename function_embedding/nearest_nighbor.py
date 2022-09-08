from typing import List, Callable

from sklearn import neighbors

from tqdm import tqdm

from collections import Counter


class GroupOfVectorsNearestNeighbors:
    # def __init__(self, victors_group_distance="naive"):
    def __init__(self, distance_function):
        # self.model = neighbors.KNeighborsClassifier(metric="precomputed")
        # self.model = neighbors.KNeighborsClassifier(n_neighbors=1, algorithm='brute', metric=distance_function)
        # self.model = neighbors.KNeighborsClassifier(n_neighbors=1, metric=distance_function)

        self.X: [dict, List] = None
        self.y: dict = None
        # self.vector_similatiry = "cosine"
        self.minimal_number_of_vectors = 100
        # self.victors_group_distance = victors_group_distance
        self.distance_function = distance_function
        self.K = 5

    # @staticmethod
    # def distance_naive(group_of_vectors_1: List, group_of_vectors_2: List):
    #     if len(group_of_vectors_1) <= len(group_of_vectors_2):
    #         query_group = group_of_vectors_1
    #         other_group = group_of_vectors_2
    #     else:
    #         query_group = group_of_vectors_2
    #         other_group = group_of_vectors_1

    #     distance_matrix = compute_distance_matrix(query_group, other_group)
    #     per_function_min = distance_matrix.min(axis=1)
    #     distance = sum_squer(per_function_min)
    #     return distance

    def fit(self, X: [dict, List], y: dict):
        self.X = self.filter_bad_groups_of_vectors(X)
        self.y = y

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
