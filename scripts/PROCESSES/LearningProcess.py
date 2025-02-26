import random
import string
from multiprocessing import Process

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

from scripts.MODEL.ClfTester import ClfTester


class LearningProcess(Process):
    def __init__(self, param_grid, x_train, y_train, x_test, y_test, x_full, y_full,
                 enable_kfold, kfold, return_dict, queue, **kwargs):
        super().__init__(**kwargs)
        self.param_grid = param_grid
        self.queue = queue
        self.X_train = x_train
        self.X_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        self.X_full = x_full
        self.y_full = y_full
        self.enable_kfold = enable_kfold
        self.kfold = kfold
        self.return_dict = return_dict
        
    def run(self):
        for param_combination in self.param_grid:
            rfc = RandomForestClassifier()
            
            rfc.set_params(**param_combination)
            clf_tester = ClfTester(rfc)
            
            clf_tester.train(self.X_train, self.y_train)
            clf_tester.test(self.X_test, self.y_test)
            
            train_scores = []
            test_scores = []
            cv_scores = []
            if not clf_tester.trained:
                train_scores.append(clf_tester.train_acc)
            test_scores.append(clf_tester.test_acc)
            # kfold
            if self.enable_kfold:
                cv_scores = cross_val_score(clf_tester.clf, self.X_full, self.y_full, cv=int(self.kfold))
            
            
            formatted_metrics = (param_combination, cv_scores, clf_tester.train_acc, clf_tester.test_acc, rfc)
            
            valid_key = False
            random_str = ''
            while not valid_key:
                random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                if random_str not in self.return_dict.keys():
                    valid_key = True
            
            self.return_dict[random_str] = formatted_metrics
            self.queue.put(1)

    