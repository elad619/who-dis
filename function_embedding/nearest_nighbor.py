from sklearn import neighbors


class GroupOfVectorsNearestNeighbors:
    def __init__(self):
        self.model = neighbors.KNeighborsClassifier(metric="precomputed")

