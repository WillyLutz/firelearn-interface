import logging

import numpy as np
from PyQt6.QtWidgets import QApplication

from QtScripts.CONTROLLER.RfcController import RfcController
from QtScripts.CONTROLLER.SvcController import SvcController
from QtScripts.CONTROLLER.UtilitiesController import UtilitiesController
from QtScripts.MODEL.LearningModel import LearningModel
from QtScripts.VIEW.LearningView import LearningView

logger = logging.getLogger("__Learning__")


class LearningController:
    def __init__(self, app: QApplication, parent_controller):
        self.app = app
        self.parent_controller = parent_controller
        self.model = LearningModel(self)  # set model
        
        self.view = LearningView(self.app, parent=self.parent_controller.view.learning_tab, controller=self)
        
        self.utilities_controller = UtilitiesController(self.app, self)
        self.rfc_controller = RfcController(self.app, self)
        self.svc_controller = SvcController(self.app, self)
    
    @staticmethod
    def label_encoding(y):
        """
        Encodes the labels in the input list to numeric values.

        Parameters
        ----------
        y : DataFrame
            Column containing the labels to be encoded.

        Returns
        -------
        y : DataFrame
            The encoded labels.
        """
        labels = list(set(list(y)))
        corr = {}
        for lab in range(len(labels)):
            corr[labels[lab]] = lab
        
        for key, value in corr.items():
            y.replace(key, value)
        
        return y
    
    @staticmethod
    def deprecated_compute_trust_score(train_score, test_score, all_cv_scores):
        kcv = np.mean(all_cv_scores)
        kcv_std = np.std(all_cv_scores)
        kfold_acc_diff = np.abs(round(train_score - kcv, 3))
        
        kfold_acc_relative_diff = round(kfold_acc_diff / train_score * 100, 2)
        return (test_score * kfold_acc_relative_diff) / (1 + np.abs(train_score - test_score) + kcv_std)

    @staticmethod
    def compute_normalized_trust(acc_train, acc_test, acc_kfolds, alpha=0.5, beta=0.2, gamma=0.3):
    
        mean_kfold = np.mean(acc_kfolds)
        std_kfold = np.std(acc_kfolds)
        gap_train_test = abs(acc_train - acc_test)
        gap_test_kfold = abs(acc_test - mean_kfold)
        gap_train_kfold = abs(acc_train - mean_kfold)
    
        cms_raw = (
            acc_test
            - alpha * gap_train_test
            - beta * std_kfold
            - gamma * (gap_test_kfold + gap_train_kfold) / 2
        )
    
        # Valeurs théoriques min et max du CMS brut
        cms_min = -alpha - 0.5 * beta - gamma
        cms_max = 1.0
    
        # Normalisation entre 0 et 1
        cms_normalized = (cms_raw - cms_min) / (cms_max - cms_min)
        return cms_normalized