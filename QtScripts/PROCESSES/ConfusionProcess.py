import logging

import numpy as np
import pandas as pd
from PyQt6.QtCore import pyqtSignal, QThread

logger = logging.getLogger("__ConfusionProcess__")

class ConfusionProcess(QThread):
    progress_made = pyqtSignal(int)
    finished = pyqtSignal(str, object, object, object, object, object,)
    error_occurred = pyqtSignal(str, str)
    cancelled = pyqtSignal()

    def __init__(self,name, train_targets, test_targets, classifier, dataset, model_vars, parent=None):
        super().__init__(parent)
        self.name = name
        self.train_targets = train_targets
        self.test_targets = test_targets
        self.classifier = classifier
        self.dataset = dataset
        self.model_vars = model_vars
        self._stop_flag = False
        self.TRAIN_CORRESPONDENCE = {}
        self.TEST_CORRESPONDENCE = {}

    def stop(self):
        self._stop_flag = True

    def run(self):
        for _ in range(1):
            if self._stop_flag:
                self.cancelled.emit()
                break
            overall_matrix_numeric, overall_matrix_percent, overall_matrix_cup \
                = self._test_clf_by_confusion(self.dataset, training_targets=self.train_targets,
                                              testing_targets=self.test_targets,
                                              )
            
            if self._stop_flag:
                self.cancelled.emit()
                break
            
            self.finished.emit(self.objectName(), overall_matrix_numeric, overall_matrix_percent, overall_matrix_cup,
                               self.TRAIN_CORRESPONDENCE, self.TEST_CORRESPONDENCE)
        
    def _test_clf_by_confusion(self, test_dataset: pd.DataFrame, training_targets, testing_targets,
                               **kwargs):
        """
        Tests a trained Random Forest classifier model using a confusion matrix.

        This method evaluates the classifier on a test full_dataset, which can have different
        target labels than those used for training. The confusion matrix and relevant
        performance metrics are computed.

        Parameters
        ----------
        test_dataset : pd.DataFrame
            Contains the test data. Each row represents an entry, while
            the columns correspond to the features on which the model was trained.
            The last column should be 'label', containing the target labels.

        training_targets : list[str]
            The target labels used during model training.

        testing_targets : list[str]
                    The target labels for testing. Can be different from `training_targets`.

        iterations : int, optional, default=10
            Number of iterations to run the test.

        Returns
        -------
        tuple of pd.DataFrame
            df_acc_numeric : pd.DataFrame
                Confusion matrix with raw count values.

            df_acc_percent : pd.DataFrame
                Confusion matrix with percentage-based accuracy values.

            df_cup : pd.DataFrame
                Matrix containing mean prediction probabilities (CUP).


        Notes
        -----
        - The function assumes a trained Random Forest classifier is already loaded in `self.model.clf`.
        - The test full_dataset must contain all necessary features for inference.
        - If `iterations` is greater than 1, the test runs multiple times for better statistical representation.

        """
        print("Process train", self.train_targets, "process test", self.test_targets)
        for _ in range(1):
            if self._stop_flag:
                self.cancelled.emit()
                break
            
            
            if not testing_targets:
                testing_targets = training_targets
            
            self._init_train_and_test_correspondence(training_targets, testing_targets)
            
            if self._stop_flag:
                self.cancelled.emit()
            X = test_dataset.loc[:, ~test_dataset.columns.isin([self.model_vars["specific_target_col_cbbox"],])]
            y = test_dataset[self.model_vars["specific_target_col_cbbox"]]
            
            X.reset_index(drop=True, inplace=True)
            
            if self._stop_flag:
                self.cancelled.emit()
                break
            self.progress_made.emit(1)
            
            # get predictions and probabilities
            all_matrices = []
            all_probability_matrices = []
            
            if self._stop_flag:
                self.cancelled.emit()
                break
    
            if self._stop_flag:
                self.cancelled.emit()
                break
            predictions = self.predict_X_values(X)
            
            targets = []
            for i in y.index:
                targets.append(y.loc[i])
            
            matrix, mean_probabilities = self._build_confusion_matrix(predictions, targets, training_targets,
                                                                      testing_targets)
            if self._stop_flag:
                self.cancelled.emit()
                break
            all_matrices.append(matrix)
            all_probability_matrices.append(mean_probabilities)
            if self._stop_flag:
                self.cancelled.emit()
                break
            mean_probabilities_matrix = np.empty((len(training_targets), len(testing_targets)))
            overall_matrix = np.mean(np.array([i for i in all_matrices]), axis=0)
            overall_probabilities = np.mean(np.array([i for i in all_probability_matrices]), axis=0)
            accuracies_percent = np.empty((len(training_targets), len(testing_targets))).tolist()
            accuracies_numeric = np.empty((len(training_targets), len(testing_targets))).tolist()
            
            if self._stop_flag:
                self.cancelled.emit()
                break
            # averaging the probabilities
            for i in range(len(overall_probabilities)):
                for j in range(len(overall_probabilities[i])):
                    mean_probabilities_matrix[i][j] = np.mean(overall_probabilities[i][j])
                    if self._stop_flag:
                        self.cancelled.emit()
                        break
                    self.progress_made.emit(1)
            
            # mixing count and probabilities for displaying
            accuracies_percent, accuracies_numeric, cups = (
                self._mix_counts_and_probs(overall_matrix, mean_probabilities_matrix, accuracies_numeric,
                                           accuracies_percent))
            
            if self._stop_flag:
                self.cancelled.emit()
                break
            columns = [x for x in self.TEST_CORRESPONDENCE.keys()]
            indexes = [x for x in self.TRAIN_CORRESPONDENCE.keys()]
            df_acc_percent = pd.DataFrame(columns=columns, index=indexes, data=accuracies_percent)
            df_acc_numeric = pd.DataFrame(columns=columns, index=indexes, data=accuracies_numeric)
            
            df_cup = pd.DataFrame(columns=columns, index=indexes, data=cups)
            df_acc_percent.index.name = "Train label"
            df_acc_numeric.index.name = "Train label"
            df_cup.index.name = "Train label"
            if self._stop_flag:
                self.cancelled.emit()
                break
            self.progress_made.emit(1)
            
            return df_acc_numeric, df_acc_percent, df_cup,
        print("reached error")
        self.error_occurred.emit("", "code is not supposed to be reached")
        return None
    
    def _init_train_and_test_correspondence(self, training_targets, testing_targets):
        """
        Initialize TRAIN_CORRESPONDENCE and TEST_CORRESPONDENCE of the train and test targets.

        Parameters
        ----------
        training_targets : list[str]
              List of unique class labels used for training.

        testing_targets : list[str]
          List of unique class labels used for testing.

        Returns
        -------

        """
        self.TRAIN_CORRESPONDENCE.clear()
        self.TEST_CORRESPONDENCE.clear()
        
        train_target_id = 0
        test_target_id = 0
        for t in training_targets:
            if t not in self.TRAIN_CORRESPONDENCE:
                self.TRAIN_CORRESPONDENCE[t] = train_target_id
                train_target_id += 1
        for t in testing_targets:
            if t not in self.TEST_CORRESPONDENCE:
                self.TEST_CORRESPONDENCE[t] = test_target_id
                test_target_id += 1
        
        if not self.TEST_CORRESPONDENCE:
            self.TEST_CORRESPONDENCE = self.TRAIN_CORRESPONDENCE.copy()

    def predict_X_values(self, X):
        """
        Predict the values for a given dataframe `X` using the trained classifier.

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe containing all the entries that need to be predicted.

        Returns
        -------
        predictions : list of tuple of size 2
            List of tuples containing the predicted class label (`y_pred`) as the first element
            and the associated probabilities for all classes (`proba_class`) as the second element.
        """
        predictions = []
        for i in range(len(X.values)):
            row = X.iloc[i]
            y_pred = self.classifier.predict([row])[0]
            proba_class = self.classifier.predict_proba([row])[0]
            predictions.append((y_pred, proba_class))
            self.progress_made.emit(1)
            if self._stop_flag:
                self.cancelled.emit()

        return predictions
    
    def _mix_counts_and_probs(self, overall_matrix, mean_probabilities_matrix,
                              accuracies_numeric, accuracies_percent, ):
        """
        Combines count-based confusion matrix values with probability-based metrics (CUP).

        Parameters
        ----------
        overall_matrix : np.ndarray
            Confusion matrix with raw count values.

        mean_probabilities_matrix : np.ndarray
            Matrix containing the mean probabilities of predictions.

        accuracies_numeric : np.ndarray
            Numeric confusion matrix (integer values).

        accuracies_percent : np.ndarray
            Percentage-based confusion matrix.

        Returns
        -------
        cups : list
            Matrix containing CUP values (rounded mean probabilities).
        """
        total_per_column = np.sum(overall_matrix, axis=0, where=overall_matrix != 0)  # Avoid division by zero
        cups = [[0] * overall_matrix.shape[1] for _ in range(overall_matrix.shape[0])]
        
        for i in range(len(overall_matrix)):
            for j in range(len(overall_matrix[i])):
                count_value = np.nan_to_num(overall_matrix[i][j])  # Ensure no NaNs
                mean_prob = np.nan_to_num(mean_probabilities_matrix[i][j])
                
                # Calculate CUP (mean probability), but only if count > 0
                CUP = round(float(mean_prob), 3) if int(count_value) != 0 else 0
                
                # Calculate percentage accuracy, ensuring no division by zero
                if int(count_value) != 0 and total_per_column[j] > 0:
                    percent = round(int(count_value) / total_per_column[j] * 100, 1)
                else:
                    percent = "0"
                
                accuracies_numeric[i][j] = int(count_value)
                accuracies_percent[i][j] = percent
                cups[i][j] = CUP
                
                if self._stop_flag:
                    return None, None, None
                self.progress_made.emit(1)
        return accuracies_percent, accuracies_numeric, cups
    
    def _build_confusion_matrix(self, predictions, targets, training_targets, testing_targets):
        """
          Builds a confusion matrix and computes the mean probabilities of predictions for each class.

          Parameters
          ----------
          predictions : list of tuple
              Each element is a tuple containing predicted label and its associated probabilities.

          targets : list[int]
              List of true labels for the full_dataset.

          training_targets : list[str]
              List of unique class labels used for training.

          testing_targets : list[str]
              List of unique class labels used for testing.

          Returns
          -------
          matrix : np.ndarray
              A confusion matrix counting the occurrences of predicted vs true labels.

          mean_probabilities : np.ndarray
              A matrix containing the mean probabilities for each predicted vs true label combination.
          """
        for _ in range(1):
            if self._stop_flag:
                self.cancelled.emit()
                break
            matrix = np.zeros((len(training_targets), len(testing_targets)))
            
            probabilities_matrix = np.empty((len(training_targets), len(testing_targets)), dtype=object)
            if self._stop_flag:
                self.cancelled.emit()
                break
            # Initializing the matrix containing the probabilities
            for i in range(len(probabilities_matrix)):
                for j in range(len(probabilities_matrix[i])):
                    probabilities_matrix[i][j] = []
            
            if self._stop_flag:
                self.cancelled.emit()
                break
            for i in range(len(targets)):
                y_true = targets[i]
                y_pred = predictions[i][0]
                y_proba = max(predictions[i][1])
                matrix[self.TRAIN_CORRESPONDENCE[y_pred]][self.TEST_CORRESPONDENCE[y_true]] += 1
                
                probabilities_matrix[self.TRAIN_CORRESPONDENCE[y_pred]][self.TEST_CORRESPONDENCE[y_true]].append(y_proba)
            
            if self._stop_flag:
                self.cancelled.emit()
                break
            mean_probabilities = np.zeros((len(training_targets), len(testing_targets)))
            
            for i in range(len(probabilities_matrix)):
                for j in range(len(probabilities_matrix[i])):
                    mean_probabilities[i][j] = np.mean(probabilities_matrix[i][j])
            if self._stop_flag:
                self.cancelled.emit()
                break
            self.progress_made.emit(1)
            
            return matrix, mean_probabilities
        
        return None, None