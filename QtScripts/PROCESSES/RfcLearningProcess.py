import logging
import random
import string

import numpy as np
import pandas as pd
from PyQt6.QtCore import pyqtSignal, QThread
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import f1_score, recall_score, precision_score

logger = logging.getLogger("__RfcLearningProcess__")
class RfcLearningProcess(QThread):
    result_ready = pyqtSignal(str, object)
    progress_made = pyqtSignal(int)
    finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str, str)
    cancelled = pyqtSignal()
    
    def __init__(self, params_queue, x_train, y_train, x_test, y_test, model_vars, **kwargs):
        super().__init__(**kwargs)

        self.X_train = x_train
        self.X_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        self.model_vars = model_vars
        self.params_queue = params_queue

        self.train_acc = 0
        self.train_metrics = {}
        self.test_acc = 0
        self.test_metrics = {}
        self.performance_metrics = {}

        self.iter = 0
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def run(self):
        while not self._stop_flag:
            try:
                if self.params_queue.empty():
                    break
                    
                combination = self.params_queue.get_nowait()
                if combination is None:
                    break
                
                random_key, result = self._learning(combination)
                
                if self._stop_flag:
                    break
                    
                self.result_ready.emit(random_key, result)
                self.progress_made.emit(1)
                logger.info(f"Worker {self.objectName()} DONE - params queue size: {self.params_queue.qsize()}")
            except Exception as e:
                logger.exception(f"Worker {self.objectName()} encountered an error.")
                self.error_occurred.emit(self.objectName(), str(e))
                break
        
        if self._stop_flag:
            self.cancelled.emit()
        else:
            self.finished.emit(self.objectName())

    def _learning(self, param_combination):
        formatted_metrics = []
        key_str = ""
        for _ in range(1):
            rfc = RandomForestClassifier()

            rfc.set_params(**param_combination)
            # clf_tester = ClfTester(rfc)
            if self._stop_flag:
                logger.info(f"{self.objectName()} cancelled")
                break
            rfc = self.train(self.X_train, self.y_train, rfc)
            if self._stop_flag:
                logger.info(f"{self.objectName()} cancelled")
                break
            self.test(self.X_test, self.y_test, rfc)

            train_scores = []
            test_scores = []
            cv_scores = []

            train_scores.append(self.train_acc)

            test_scores.append(self.test_acc)
            # kfold
            if self._stop_flag:
                logger.info(f"{self.objectName()} cancelled")
                break
            if self.model_vars["learn_kfold_ckbox"]:
                X_full = pd.concat([self.X_train, self.X_test], ignore_index=True)
                y_full = pd.concat([self.y_train, self.y_test], ignore_index=True)
                cv_scores = cross_val_score(rfc, X_full, y_full, cv=int(self.model_vars["learn_kfold_edit"]))
            # self.progress_queue.put(1)
            
            self.performance_metrics_computation(self.X_test, self.y_test, rfc)
            
            formatted_metrics = (param_combination, cv_scores, self.train_acc, self.test_acc, rfc, self.performance_metrics)

            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            key_str = f"{self.objectName()}-{self.iter}-{random_str}"
            self.iter += 1
            # self.progress_queue.put(1)

            return key_str, formatted_metrics
        return "False", False

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

    def performance_metrics_computation(self, X, y, clf):
        
        y_preds = clf.predict(X)
        
        self.performance_metrics["f1-score"] = round(f1_score(y_true=y, y_pred=y_preds, average="macro"), 3)
        self.performance_metrics["recall"] = round(recall_score(y_true=y, y_pred=y_preds, average="macro"), 3)
        self.performance_metrics["precision"] = round(precision_score(y_true=y, y_pred=y_preds, average="macro"), 3)
