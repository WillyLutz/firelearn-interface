import random
import string
import threading
from multiprocessing import Process

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

import logging
logger = logging.getLogger("__LearningProcess__")
class LearningProcess(threading.Thread):
    def __init__(self, params_queue, result_queue, progress_queue, x_train, y_train, x_test, y_test, x_full, y_full,
                 enable_kfold, kfold, lock, **kwargs):
        super().__init__(**kwargs)

        self.X_train = x_train
        self.X_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        self.X_full = x_full
        self.y_full = y_full
        self.enable_kfold = enable_kfold
        self.kfold = kfold
        self.params_queue = params_queue
        self.result_queue = result_queue
        self.progress_queue = progress_queue

        self.train_acc = 0
        self.train_metrics = {}
        self.test_acc = 0
        self.test_metrics = {}

        self.iter = 0

        self.lock = lock
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        self._learning_for_worker()
        self.result_queue.put(self.name, timeout=10)
        logger.info(f"Prisoner {self.name} has exited")

    def _learning_for_worker(self):

        while True:
            try:
                if self.stopped():
                    logger.info(self.name, "cancelled")
                    break

                combination = self.params_queue.get(timeout=1)
                # check for sentinel value
                if combination is None:
                    logger.info(f"Worker {self.name} received stop signal and is exiting gracefully.")
                    break

                random_key, result = self._learning(combination)

                if self.result_queue.full():
                    logger.info(f"Worker {self.name} encountered an error adding results of {combination}:")

                if self.stopped():
                    logger.info(self.name, "cancelled")
                    break
                self.result_queue.put((random_key, result), timeout=10)
                with self.lock:
                    self.progress_queue.put(1)
                logger.info(f"Worker {self.name} DONE - params queue size: {self.params_queue.qsize()}")
            except Exception as e:
                logger.info(f"Worker {self.name} encountered an error. Terminating. {e}")
                break
        logger.info(f"Worker {self.name} exiting. Final params queue size: {self.params_queue.qsize()}")

    def _learning(self, param_combination):
        formatted_metrics = []
        key_str = ""
        for _ in range(1):
            rfc = RandomForestClassifier()

            rfc.set_params(**param_combination)
            # clf_tester = ClfTester(rfc)
            if self.stopped():
                logger.info(self.name, "cancelled")
                break
            rfc = self.train(self.X_train, self.y_train, rfc)
            if self.stopped():
                logger.info(self.name, "cancelled")
                break
            self.test(self.X_test, self.y_test, rfc)

            train_scores = []
            test_scores = []
            cv_scores = []

            train_scores.append(self.train_acc)

            test_scores.append(self.test_acc)
            # kfold
            if self.stopped():
                logger.info(self.name, "cancelled")
                break
            if self.enable_kfold:
                cv_scores = cross_val_score(rfc, self.X_full, self.y_full, cv=int(self.kfold))
            # self.progress_queue.put(1)

            formatted_metrics = (param_combination, cv_scores, self.train_acc, self.test_acc, rfc)

            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            key_str = f"{self.name}-{self.iter}-{random_str}"
            self.iter += 1
            # self.progress_queue.put(1)

            return key_str, formatted_metrics

    def train(self, X, y, clf):
        labels = list(set(list(y)))

        for label in labels:
            self.train_metrics[label] = {"true": [], "false": []}

        clf.fit(np.array(X), np.array(y))
        # self.progress_queue.put(1)

        self.train_metrics = self.test_classifier(X, y, clf)
        # self.progress_queue.put(1)

        self.train_acc = self.accuracy_computation(self.train_metrics)
        # self.progress_queue.put(1)

        return clf

    def test(self, X, y, clf):
        labels = list(set(list(y)))
        for label in labels:
            self.test_metrics[label] = {"true": [], "false": []}

        self.test_metrics = self.test_classifier(X, y, clf)
        # self.progress_queue.put(1)

        self.test_acc = self.accuracy_computation(self.test_metrics)
        # self.progress_queue.put(1)

    def test_classifier(self, X, y, clf):
        labels = list(set(list(y)))
        metrics = {}
        for label in labels:
            metrics[label] = ([], [])

        for i in X.index:
            row = np.array(X.loc[i, :])
            y_pred = clf.predict([row])[0]
            proba_class = clf.predict_proba([row])[0]

            y_true = y.loc[i]
            y_proba = max(proba_class)

            if y_true == y_pred:
                metrics[y_true][0].append(y_proba)
            else:
                metrics[y_pred][1].append(y_proba)
            # # self.progress_queue.put(1)

        return metrics

    @staticmethod
    def accuracy_computation(metrics):
        true_preds = []
        false_preds = []
        for target, target_metric in metrics.items():
            true_preds.append(len(target_metric[0]))
            false_preds.append(len(target_metric[1]))

        return round(sum(true_preds, 0) / (sum(true_preds, 0) + sum(false_preds, 0)), 3)
