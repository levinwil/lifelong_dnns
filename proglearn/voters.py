'''
Main Author: Will LeVine 
Corresponding Email: levinewill@icloud.com
'''
import numpy as np

from sklearn.neighbors import KNeighborsClassifier

from sklearn.utils.validation import (
    check_X_y,
    check_array,
    NotFittedError,
)

from sklearn.utils.multiclass import check_classification_targets

from .base import BaseVoter


class TreeClassificationVoter(BaseVoter):
    def __init__(self, finite_sample_correction=False):
        """
        Doc strings here.
        """

        self.finite_sample_correction = finite_sample_correction
        self._is_fitted = False

    def fit(self, X, y):
        """
        Doc strings here.
        """
        check_classification_targets(y)

        num_classes = len(np.unique(y))
        self.uniform_posterior = np.ones(num_classes) / num_classes

        self.leaf_to_posterior = {}

        for leaf_id in np.unique(X):
            idxs_in_leaf = np.where(X == leaf_id)[0]
            class_counts = [
                len(np.where(y[idxs_in_leaf] == y_val)[0]) for y_val in np.unique(y)
            ]
            posteriors = np.nan_to_num(np.array(class_counts) / np.sum(class_counts))

            if self.finite_sample_correction:
                posteriors = self._finite_sample_correction(
                    posteriors, len(idxs_in_leaf), len(np.unique(y))
                )

            self.leaf_to_posterior[leaf_id] = posteriors

        self._is_fitted = True

        return self

    def vote(self, X):
        """
        Doc strings here.
        """

        if not self.is_fitted():
            msg = (
                "This %(name)s instance is not fitted yet. Call 'fit' with "
                "appropriate arguments before using this voter."
            )
            raise NotFittedError(msg % {"name": type(self).__name__})

        votes_per_example = []
        for x in X:
            if x in list(self.leaf_to_posterior.keys()):
                votes_per_example.append(self.leaf_to_posterior[x])
            else:
                votes_per_example.append(self.uniform_posterior)
        return np.array(votes_per_example)

    def is_fitted(self):
        """
        Doc strings here.
        """

        return self._is_fitted

    def _finite_sample_correction(posteriors, num_points_in_partition, num_classes):
        """
        encourage posteriors to approach uniform when there is low data
        """
        correction_constant = 1 / (num_classes * num_points_in_partition)

        zero_posterior_idxs = np.where(posteriors == 0)[0]
        posteriors[zero_posterior_idxs] = correction_constant

        posteriors /= sum(posteriors)

        return posteriors


class KNNClassificationVoter(BaseVoter):
    def __init__(self, k=None, kwargs={}):
        """
        Doc strings here.
        """
        self._is_fitted = False
        self.k = k
        self.kwargs = kwargs

    def fit(self, X, y):
        """
        Doc strings here.
        """
        X, y = check_X_y(X, y)
        k = int(np.log2(len(X))) if self.k == None else self.k
        self.knn = KNeighborsClassifier(k, **self.kwargs)
        self.knn.fit(X, y)
        self._is_fitted = True

        return self

    def vote(self, X):
        """
        Doc strings here.
        """
        if not self.is_fitted():
            msg = (
                "This %(name)s instance is not fitted yet. Call 'fit' with "
                "appropriate arguments before using this transformer."
            )
            raise NotFittedError(msg % {"name": type(self).__name__})

        X = check_array(X)
        return self.knn.predict_proba(X)

    def is_fitted(self):
        """
        Doc strings here.
        """

        return self._is_fitted
