import logging
import pickle

import numpy as np
import pandas as pd
import seaborn as sns
from PyQt6.QtWidgets import QApplication, QMessageBox

from QtScripts.MODEL.ConfusionModel import ConfusionModel
from QtScripts.PROCESSES.ConfusionProcess import ConfusionProcess
from QtScripts.VIEW.ConfusionView import ConfusionView

logger = logging.getLogger("__Confusion__")


class ConfusionController:
    def __init__(self, app: QApplication, parent_controller):
        self.app = app
        self.parent_controller = parent_controller
        self.model = ConfusionModel(self)  # set model
        self.view = ConfusionView(self.app, parent=self.parent_controller.view.confusion_tab, controller=self)
        self.confusion_thread = None
        self.results = {}
        
    def _check_computation_compatible(self):
        errors = []
        # check if some inputs have been changed since computation
        overall_matrix_percent = self.results["overall_matrix_percent"]
        overall_matrix_numeric = self.results["overall_matrix_numeric"]
        overall_matrix_cup = self.results["overall_matrix_cup"]
        TRAIN_CORRESPONDENCE = self.results["TRAIN_CORRESPONDENCE"]
        TEST_CORRESPONDENCE = self.results["TEST_CORRESPONDENCE"]
        
        view_test_target = {key: value for key, value in self.view.widgets.items() if
                       "confusion_table_test_ckbox_" in key}
        view_checked_test_targets = [key for key, value in view_test_target.items() if value.isChecked()]
        model_test_target = {key: value for key, value in self.model.widgets_values.items() if
                            "confusion_table_test_ckbox_" in key}
        model_checked_test_targets = [key for key, value in model_test_target.items() if value]
        if view_checked_test_targets != model_checked_test_targets:
            errors.append("Testing targets have been changed since last computation.")
        
            
        if errors:
            errors.insert(0, "Some changed parameters are incompatible with the previously computed matrix. Please run"
                          " a new computation to use the specified parameters.", )
            QMessageBox.critical(self.view, "Input Errors", "\n".join(errors))
            return False
        else:
            return True
        
    def draw(self):
        if self._check_computation_compatible():

            self.update_model_from_view()
            if self._check_params():
                if not self.results:
                    QMessageBox.information(self.parent_controller.view, "Confusion Results", f"No results found.")
                    return
                
                self.view.figure.clf()
                self.view.ax.clear()
                
                self.view.ax = self.view.figure.add_subplot(111)
        
                overall_matrix_percent = self.results["overall_matrix_percent"]
                overall_matrix_numeric = self.results["overall_matrix_numeric"]
                overall_matrix_cup = self.results["overall_matrix_cup"]
                TRAIN_CORRESPONDENCE = self.results["TRAIN_CORRESPONDENCE"]
                TEST_CORRESPONDENCE = self.results["TEST_CORRESPONDENCE"]
                
                annotation_mode = self.model.widgets_values["specific_annotation_cbbox"]
                overall_matrix = overall_matrix_percent \
                    if annotation_mode == 'percent' \
                    else overall_matrix_numeric
                
                
                acc_array = overall_matrix.to_numpy().astype(float) if annotation_mode == 'percent' else overall_matrix.to_numpy().astype(
                    int)
                cup_array = overall_matrix_cup.to_numpy()
                mixed_labels_matrix = np.empty((len(TRAIN_CORRESPONDENCE.keys()), len(TEST_CORRESPONDENCE.keys()))).tolist()
                
                compute_train_index_to_plot_index = {}
                compute_test_index_to_plot_index = {}
                
                test_target_ckboxes = {key: value for key, value in self.model.widgets_values.items() if
                               "confusion_table_test_ckbox_" in key}
                checked_test_targets = [key for key, value in test_target_ckboxes.items() if value]
                test_target_label = []
                for checked in checked_test_targets:
                    test_target_label.append(self.view.widgets[checked].text())
                    
                for label_index in range(len(self.model.train_targets)):
                    plot_index = int(self.model.widgets_values[f"confusion_table_train_cbbox_{label_index}"])
                    compute_index = label_index
                    compute_train_index_to_plot_index[compute_index] = plot_index
                
                confusion_index = 0
                for label_index, k in enumerate(test_target_ckboxes.keys()):
                    # plot_index = int(self.view.vars[f"test label {t} index"].get())
                    if k in checked_test_targets:
                        plot_index = int(self.model.widgets_values[f"confusion_table_test_cbbox_{label_index}"])
                        compute_index = label_index
                        compute_test_index_to_plot_index[confusion_index] = plot_index
                        confusion_index += 1

                if (not self.parent_controller.parent_controller.has_unique_second_elements(compute_train_index_to_plot_index)
                        or not self.parent_controller.parent_controller.has_unique_second_elements(
                        TRAIN_CORRESPONDENCE)):
                    QMessageBox.critical(self.view, 'Unique Values', 'You can not have multiple training targets having the same index.')
                    return
                if (not self.parent_controller.parent_controller.has_unique_second_elements(compute_test_index_to_plot_index)
                        or not self.parent_controller.parent_controller.has_unique_second_elements(
                        TEST_CORRESPONDENCE)):
                    QMessageBox.critical(self.view, 'Unique Values', 'You can not have multiple testing targets having the same index.')
                    return
                
                translated_train_correspondence = {v: k for k, v in TRAIN_CORRESPONDENCE.items()}
                translated_test_correspondence = {v: k for k, v in TEST_CORRESPONDENCE.items()}
                
                translated_acc_array = acc_array.copy()
                for r in range(len(acc_array)):
                    for c in range(len(acc_array[0])):
                        translated_r = compute_train_index_to_plot_index[r]
                        translated_c = compute_test_index_to_plot_index[c]
                        translated_acc_array[translated_r][translated_c] = acc_array[r][c]
                
                for r in range(len(acc_array)):
                    for c in range(len(acc_array[0])):
                        if self.model.widgets_values["specific_cup_ckbox"]:
                            case = f"{cup_array[r][c]}"
                            mixed_labels_matrix[r][c] = case
                        else:
                            if self.model.widgets_values["specific_annotation_cbbox"] == 'percent':
                                case = f"{acc_array[r][c]}%\nCUP={cup_array[r][c]}"
                            elif self.model.widgets_values["specific_annotation_cbbox"] == 'numeric':
                                 case =  f"{acc_array[r][c]}\nCUP={cup_array[r][c]}"
                            else:
                                case = f"{acc_array[r][c]}"
                            mixed_labels_matrix[r][c] = case
                
                translated_mixed_labels_matrix = [row.copy() for row in mixed_labels_matrix]

                for r in range(len(acc_array)):
                    for c in range(len(acc_array[0])):
                        translated_r = compute_train_index_to_plot_index[r]
                        translated_c = compute_test_index_to_plot_index[c]
                        translated_mixed_labels_matrix[translated_r][translated_c] = mixed_labels_matrix[r][c]
                
                
                
                annot_kws = {"font": self.model.widgets_values["plot_axes_font_cbbox"],
                             "size": self.model.widgets_values["specific_annotation_size_slider"]}
                
                if self.model.widgets_values["specific_annotation_cbbox"] == 'percent':
                    heatmap = sns.heatmap(ax=self.view.ax, data=translated_acc_array, annot=translated_mixed_labels_matrix, annot_kws=annot_kws, fmt='',
                                cmap=self.model.widgets_values["plot_colorbar_cbbox"],
                                square=True, cbar_kws={'shrink': 0.5, 'location': 'right'}, cbar=False,
                                          vmin=0, vmax=100)
                else:
                    heatmap = sns.heatmap(ax=self.view.ax, data=translated_acc_array,
                                          annot=translated_mixed_labels_matrix, annot_kws=annot_kws, fmt='',
                                          cmap=self.model.widgets_values["plot_colorbar_cbbox"],
                                          square=True, cbar_kws={'shrink': 0.5, 'location': 'right'}, cbar=False,)
                self.view.figure.colorbar(
                    heatmap.get_children()[0],   # pass the AxesImage or QuadMesh
                    ax=self.view.ax,
                    shrink=0.5,
                )
                self.view.ax.xaxis.tick_top()
                self.view.ax.xaxis.set_label_position('top')
                self.view.ax.set_ylabel(self.model.widgets_values["plot_y_label_edit"], fontdict={"font": self.model.widgets_values["plot_axes_font_cbbox"],
                                                                         "fontsize": self.model.widgets_values["plot_y_label_size_slider"]})
                self.view.ax.set_xlabel(self.model.widgets_values["plot_x_label_edit"], {"font": self.model.widgets_values["plot_axes_font_cbbox"],
                                                                "fontsize": self.model.widgets_values["plot_x_label_size_slider"]})
                
                
                
                self.view.ax.set_xticks(
                    [compute_test_index_to_plot_index[TEST_CORRESPONDENCE[x]] + 0.5 for x in self.model.test_targets],
                    self.model.test_targets,
                    fontsize=self.model.widgets_values["plot_x_tick_size_slider"], )
                self.view.ax.tick_params(axis='x', labelrotation=self.model.widgets_values["plot_x_tick_rotation_slider"],
                               labelsize=self.model.widgets_values["plot_x_tick_size_slider"],
                               labelfontfamily=self.model.widgets_values["plot_axes_font_cbbox"])
                self.view.ax.tick_params(axis='y', labelrotation=self.model.widgets_values["plot_y_tick_rotation_slider"],
                               labelsize=self.model.widgets_values["plot_y_tick_size_slider"],
                               labelfontfamily=self.model.widgets_values["plot_axes_font_cbbox"])
                
                self.view.ax.set_title(self.model.widgets_values["plot_title_edit"],
                             fontdict={"font": self.model.widgets_values["plot_title_font_cbbox"],
                                       "fontsize": self.model.widgets_values["plot_title_size_slider"]}, )
                self.view.ax.set_yticks(
                    [compute_train_index_to_plot_index[TRAIN_CORRESPONDENCE[x]] + 0.5 for x in self.model.train_targets],
                    self.model.train_targets, fontsize=self.model.widgets_values["plot_y_tick_size_slider"])
                
                self.view.figure.tight_layout()
                self.view.canvas.draw()
    
    def _check_params(self):
        errors = []
        
        if not self.model.full_dataset is not None:
            errors.append("No full_dataset loaded.")
            
        test_target = {key: value for key, value in self.model.widgets_values.items() if "confusion_table_test_ckbox_" in key}
        checked_test_targets = [key for key, value in test_target.items() if value]
        if not checked_test_targets:
            errors.append("No test targets checked.")
            
        # Check if there are doublets in checked testing targets indices
        checked_indices = []
        for key in checked_test_targets:
            checked_indices.append(int(self.model.widgets_values[key.replace("_ckbox_", "_cbbox_")]))
        if len(checked_indices) != len(list(set(checked_indices))):
            errors.append("You can not have multiple testing targets having the same index.")
        
        if max(checked_indices) > len(checked_indices)-1:
            errors.append("You specified a testing target index with a value superior than the number of checked targets.")
        
        train_cbboxes = {key: value for key, value in self.model.widgets_values.items() if "confusion_table_train_cbbox_" in key}
        train_indices = [int(value) for k, value in train_cbboxes.items()]
        if len(train_indices) != len(list(set(train_indices))):
            errors.append("You can not have multiple training targets having the same index.")
       
        if errors:
            QMessageBox.critical(self.view, "Input Errors", "\n".join(errors))
            return False
        else:
            return True
        
    def update_model_from_view(self,):
        self.parent_controller.parent_controller.update_model_from_view(self.model, self.view)
        
        test_target = {key: value for key, value in self.model.widgets_values.items() if "confusion_table_test_ckbox_" in key}
        checked_test_targets = [key for key, value in test_target.items() if value]
        test_target_label = []
        for checked in checked_test_targets:
            test_target_label.append(self.view.widgets[checked].text())
        self.model.test_targets = test_target_label
        

    def _init_progress_bar(self, sub_df):

        dataset_prep = 1
        n_test_targets = len(self.model.test_targets)
        n_train_targets = len(self.model.train_targets)
        matrix_proba_averaging = n_train_targets * n_test_targets
        prediction = len(sub_df)
        mix_counts_and_probs = n_test_targets * n_train_targets
        build_confusion_matrix = 1
        self.view.progress_bar.set_range(0, dataset_prep+matrix_proba_averaging + prediction + mix_counts_and_probs + build_confusion_matrix)
        self.view.progress_bar.set_value(0)
        
    def compute_confusion(self):
        self.update_model_from_view()
        if self._check_params():
            target_col = self.model.widgets_values["specific_target_col_cbbox"]
            sub_df = self.model.full_dataset.loc[self.model.full_dataset[target_col].astype(str).isin(self.model.test_targets)]
            sub_df[target_col] = sub_df[target_col].astype(str)
            self._init_progress_bar(sub_df)
            self.confusion_thread = ConfusionProcess(name="ConfusionWorker1",
                                                     train_targets=self.model.train_targets,
                                                     test_targets=self.model.test_targets,
                                                     dataset=sub_df,
                                                     model_vars=self.model.widgets_values,
                                                     classifier=self.model.classifier,
                                                     parent=self.view)
            
            # Connect signals to slots
            self.confusion_thread.progress_made.connect(self.handle_progress)
            self.confusion_thread.error_occurred.connect(self.handle_error)
            self.confusion_thread.finished.connect(self.handle_finished)
            self.confusion_thread.cancelled.connect(self.handle_cancel)
    
            # Start the worker thread
            self.view.progress_bar.set_task("Confusion computation...")
            self.confusion_thread.start()
            self.app.add_thread("ConfusionWorker1", self.confusion_thread)
            
    def handle_cancel(self):
        self.view.progress_bar.reset()
        self.results = {}
        QMessageBox.information(self.view, "Canceled", "Computation canceled")
        
    def handle_progress(self, count):
        self.view.progress_bar.increment_steps(count)
        logger.debug("Progress made")
        
    def handle_error(self, worker_name, error_msg):
        logger.error(f"Error from {worker_name}: {error_msg}")
        
    def handle_finished(self, worker_name, overall_matrix_numeric, overall_matrix_percent, overall_matrix_cup,
                               TRAIN_CORRESPONDENCE, TEST_CORRESPONDENCE):
    
        logger.info(f"Worker {worker_name} finished processing.")
        
        self.results["overall_matrix_numeric"] = overall_matrix_numeric
        self.results["overall_matrix_percent"] = overall_matrix_percent
        self.results["overall_matrix_cup"] = overall_matrix_cup
        self.results["TRAIN_CORRESPONDENCE"] = TRAIN_CORRESPONDENCE
        self.results["TEST_CORRESPONDENCE"] = TEST_CORRESPONDENCE
        self.view.progress_bar.reset()
        self.view.progress_bar.set_task("No Task running.")
        self.draw()
    
    def load_dataset(self):
        dialog = self.parent_controller.parent_controller.load_path_and_update_edit(
            self.view.widgets["specific_load_dataset_edit"], mode='getOpenFileName',
            filter_="Dataset (*.csv)", directory='',
        )
        if dialog:
            df = pd.read_csv(dialog, index_col=False)
            combo = self.view.widgets["specific_target_col_cbbox"]
            self.model.full_dataset = df
            
            previous_test_targets = [key for key in self.model.widgets_values.keys() if "confusion_table_test_ckbox_" in key]
            for previous_key in previous_test_targets:
                del self.view.widgets[previous_key]
                del self.model.widgets_values[previous_key]
                
            combo.currentIndexChanged.disconnect()
            combo.clear()
            columns = ["", ] + self.model.full_dataset.columns.tolist()
            combo.addItems(columns)
            combo.setCurrentText("")
            combo.currentIndexChanged.connect(self.update_target_col)
            
            autoload_col = ""
            for col in self.model.full_dataset.columns:
                if "target" in col or "label" in col:
                    autoload_col = col
            
            # self.clear_("specific_test_scroll_area")
            self.view.widgets["specific_test_confusion_table"].clear()
            self.load_test_confusion_table()
            if autoload_col:
                logger.info(f"Autoload column {autoload_col}")
                combo.setCurrentText(autoload_col)
                
            self.update_model_from_view()
                
    def load_classifier(self):
        dialog = self.parent_controller.parent_controller.load_path_and_update_edit(
            self.view.widgets["specific_load_classifier_edit"], mode='getOpenFileName',
            filter_="Model (*.rfc *.svc)", directory='',
        )
        if dialog:
            clf = pickle.load(open(dialog, "rb"))
            self.model.classifier = clf
            self.view.widgets["specific_train_confusion_table"].clear()
            self.load_train_confusion_table()
            
    
    def update_target_col(self):
        combo = self.view.widgets["specific_target_col_cbbox"]
        target_col = combo.currentText()
        
        if target_col:
            targets = list(set(list(self.model.full_dataset[target_col])))
            if len(targets) > 20:
                proceed = QMessageBox.question(self.view, "Too many targets",
                                               f"There are more than 20 ({len(targets)}) unique values in the specified"
                                               "target column. Proceed with the loading ?",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
                if proceed == QMessageBox.StandardButton.Cancel:
                    combo.setCurrentText("")
                    self.clear_("specific_test_scroll_area")
                    return
            
            self.clear_("specific_test_scroll_area")
            self.load_test_confusion_table()
            
    
    def select_all(self):
        keys = [key for key in self.view.widgets.keys() if "confusion_table_test_ckbox" in key]
        for k in keys:
            self.view.widgets[k].setChecked(True)
    
    def deselect_all(self):
        keys = [key for key in self.view.widgets.keys() if "confusion_table_test_ckbox" in key]
        for k in keys:
            self.view.widgets[k].setChecked(False)
    
    def clear_(self, name):
        # Clear layout widgets
        
        
        widgets_to_del = [key for key in list(self.view.widgets.keys())
                          if key.startswith(name + "_") and key != name]
        for w in widgets_to_del:
            widget = self.view.widgets[w]
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            del self.view.widgets[w]
            
    def load_train_confusion_table(self):
        confusion_table = self.view.widgets["specific_train_confusion_table"]
        
        training_classes = list(set(list(self.model.classifier.classes_)))
        self.model.train_targets = training_classes
        confusion_table.update_combo_items(training_classes)
        
            
    
    def load_test_confusion_table(self):
        combo = self.view.widgets["specific_target_col_cbbox"]
        target_col = combo.currentText()
        if target_col:
            testing_classes = list(set(list(self.model.full_dataset[target_col])))
            confusion_table = self.view.widgets["specific_test_confusion_table"]
            logger.info(f"load full_dataset { testing_classes}")
            self.model.test_targets = testing_classes
            confusion_table.update_combo_items(testing_classes)
    
    
