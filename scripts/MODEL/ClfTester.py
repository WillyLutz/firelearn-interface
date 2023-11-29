import pickle

import numpy as np
from sklearn.model_selection import train_test_split


class ClfTester:
    def __init__(self, clf):
        self.clf = clf
        self.clf_class = type(self.clf)

        self.train_acc = 0
        self.train_metrics = {}
        self.test_acc = 0
        self.test_metrics = {}

        self.trained = False

    def save(self, path):
        try:
            pickle.dump(self, open(path, "wb"))
            return True
        except Exception as e:
            print(e)
            return False

    def load_model(self, path):
        try:
            attr_dict = pickle.load(open(path, "rb"))
            self.__dict__.update(attr_dict)
            return True
        except Exception as e:
            print(e)
            return False

    def train_test(self, X, y):  # works only for RFC !!
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
        labels = list(set(list(y)))

        for label in labels:
            self.test_metrics[label] = {"true": [], "false": []}

        if not self.trained:
            self.clf.fit(X_train, y_train)
            self.train_metrics = self.test_classifier(X_train, y_train)
            self.train_acc = self.accuracy_computation(self.train_metrics)

        self.test_metrics = self.test_classifier(X_test, y_test)
        self.test_acc = self.accuracy_computation(self.test_metrics)

    def train(self, X, y):
        labels = list(set(list(y)))

        for label in labels:
            self.train_metrics[label] = {"true": [], "false": []}

        if not self.trained:
            self.clf.fit(np.array(X), np.array(y))
            self.train_metrics = self.test_classifier(X, y)
            self.train_acc = self.accuracy_computation(self.train_metrics)

    def test(self, X, y):
        labels = list(set(list(y)))
        for label in labels:
            self.test_metrics[label] = {"true": [], "false": []}

        self.test_metrics = self.test_classifier(X, y)
        self.test_acc = self.accuracy_computation(self.test_metrics)

    def test_classifier(self, X, y):
        labels = list(set(list(y)))
        metrics = {}
        for label in labels:
            metrics[label] = ([], [])

        for i in X.index:
            row = np.array(X.loc[i, :])
            y_pred = self.clf.predict([row])[0]
            proba_class = self.clf.predict_proba([row])[0]

            y_true = y.loc[i]
            y_proba = max(proba_class)

            if y_true == y_pred:
                metrics[y_true][0].append(y_proba)
            else:
                metrics[y_pred][1].append(y_proba)

        return metrics

    @staticmethod
    def accuracy_computation(metrics):
        true_preds = []
        false_preds = []
        for target, target_metric in metrics.items():
            true_preds.append(len(target_metric[0]))
            false_preds.append(len(target_metric[1]))

        return round(sum(true_preds, 0) / (sum(true_preds, 0) + sum(false_preds, 0)), 3)
