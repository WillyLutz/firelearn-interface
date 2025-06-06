import datetime
import logging
import multiprocessing
import random
import string

import pandas as pd
from PyQt6.QtCore import QMutex
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from fiiireflyyy import files as ff

from QtScripts.MODEL.SpikeDetectionModel import SpikeDetectionModel
from QtScripts.PROCESSES.SpikeDetector import SpikeDetectorProcess
from QtScripts.VIEW.SpikeDetectionView import SpikeDetectionView

logger = logging.getLogger("__SpikeDetection__")


class SpikeDetectionController:
    def __init__(self, app: QApplication, parent_controller):
        self.app = app
        self.parent_controller = parent_controller
        self.model = SpikeDetectionModel(self)  # set model
        
        self.files_to_process = []
        self.files_queue = None
        
        self.lock = QMutex()
        self.progress_dialog = None
        
        self.processing_thread = None
        
        self.view = SpikeDetectionView(self.app, parent=self.parent_controller.view.spike_detection_tab, controller=self)
        self.threads_alive = False
        self.cancelled = False
        self.results = {}
        self.result_headers = ["Key", "File", "Sampling frequency [Hz]", "Number of values", "Target", "Column ID",
                               "Threshold crossing index", "Peak value [###]", "Peak index",
                               "Minimum value [###]", "Maximum value [###]", "Slope", "Extrema ratio (min/max)",
                               "Extraction first index", "Extraction last index", "Extracted data [###]",]
        self.all_random_keys = []
        self.resulting_dataframe = pd.DataFrame(columns=self.result_headers, )
        
        self.processing_time_start = datetime.datetime.now()
    
    def select_parent_directory(self):
        directory = QFileDialog.getExistingDirectory(parent=self.view.parent, caption="Select Parent Directory")
        if directory:
            self.model.parent_directory = directory
            self.view.widgets["path_to_parent_edit"].setText(directory)
    
    def select_single_file_processing(self):
        file = QFileDialog.getOpenFileName(parent=self.view.parent, caption="Select Processing File")[0]
        if file:
            self.model.single_file_processing = file
            self.view.widgets["path_to_file_edit"].setText(file)
    
    def select_save_processed_files_under(self):
        directory = QFileDialog.getExistingDirectory(parent=self.view.parent, caption="Select save directory")
        if directory:
            self.model.parent_directory = directory
            self.view.widgets["save_edit"].setText(directory)
        
    def check_parameters(self):
        self.parent_controller.parent_controller.update_model_from_view(self.model, self.view)

        errors = []
        
        if self.threads_alive:
            if self.cancelled:
                QMessageBox.warning(self.view, "Warning",
                                    "Threads from previous processing are still alive and being terminated."
                                    " Please wait a bit before starting a new processing",
                                    QMessageBox.StandardButton.Ok)
                return False
            else:
                QMessageBox.warning(self.view, "Warning", "Threads are currently alive."
                                                          "To start a new processing, please either cancel the current one "
                                                          "or wait for it to finish.", QMessageBox.StandardButton.Ok)
                return False
        
        # ------- PROCESSING
        if self.model.widgets_values["detection_behead_ckbox"] and not self.model.widgets_values["detection_behead_edit"]:
            errors.append("You have to indicate a number of rows to behead the file(s).")
        
        if self.model.widgets_values["detection_column_selection_ckbox"]:
            if not self.model.widgets_values["detection_column_selection_edit"]:
                errors.append("You have to indicate a number of columns to be selected.")
        
        
        if not self.model.widgets_values["detection_save_edit"]:
            errors.append("You have to indicate a directory to save you file(s).")
        
        if not all([self.model.widgets_values["detection_behead_edit"],
                    self.model.widgets_values["detection_threshold_edit"],
                    self.model.widgets_values["detection_dead_window_edit"],
                    self.model.widgets_values["detection_extraction_min_margin_edit"],
                    self.model.widgets_values["detection_extraction_max_margin_edit"],
                    self.model.widgets_values["detection_save_edit"],
                    ]):
            errors.append("You can not leave empty edit fields.")
        
        # ------- INTERDEPENDENCIES
        if all([self.model.widgets_values["multiple_files_ckbox"],
                self.model.widgets_values["single_file_ckbox"]]):
            errors.append("You can only chose one between Single file analysis or Multiple files analysis.")
        
        if not any([self.model.widgets_values["multiple_files_ckbox"],
                    self.model.widgets_values["single_file_ckbox"]]):
            errors.append("You must chose one between Single file analysis or Multiple files analysis.")
        
        if self.model.widgets_values["multiple_files_ckbox"] and not self.model.widgets_values[
            "path_to_parent_edit"]:
            errors.append("You have to select a parent directory to run multi-file processing.")
        
        if self.model.widgets_values["single_file_ckbox"] and not self.model.widgets_values[
            "path_to_file_edit"]:
            errors.append("You have to select a file to run single-file processing.")
        
        if self.model.widgets_values["detection_extraction_ckbox"]:
            if not self.model.widgets_values["detection_extraction_min_margin_edit"]:
                errors.append("You have to indicate a minimum margin for spike extraction.")
            if not self.model.widgets_values["detection_extraction_max_margin_edit"]:
                errors.append("You have to indicate a maximum margin for spike extraction.")
                
        
        if errors:
            QMessageBox.critical(self.view, "Input Errors", "\n".join(errors))
            return False
        else:
            return True
    
    def _select_files(self):
        all_files = []
        untargeted_files = []
        if self.model.widgets_values['multiple_files_ckbox']:
            files = ff.get_all_files(self.model.widgets_values['path_to_parent_edit'], to_include=self.model.to_include,
                                     to_exclude=self.model.to_exclude)
            # files = [str(p) for p in Path(self.model.widgets_values['path_to_parent_edit']).rglob("*") if p.is_file()]
            for file in files:
                
                if any(value in file for value in self.model.targets.keys()):
                    all_files.append(file)
                else:
                    untargeted_files.append(file)
        
        if self.model.widgets_values['single_file_ckbox']:
            if any(value in self.model.widgets_values["path_to_file_edit"] for value in self.model.targets.values()):
                all_files.append(self.model.widgets_values["path_to_file_edit"])
            else:
                untargeted_files.append(self.model.widgets_values["path_to_file_edit"])
        if all_files:
            if untargeted_files:
                reply = QMessageBox.question(
                    self.view,
                    "Targets not found",
                    f"{len(untargeted_files)} file(s) contain(s) none of the targets indicated."
                    "They will be ignored. Proceed?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
                )
                if reply == QMessageBox.StandardButton.Yes:
                    all_files += untargeted_files
                    self.files_to_process = all_files
                    return True
                else:
                    return False
            else:
                self.files_to_process = all_files
                return True
        elif not all_files and untargeted_files:
            reply = QMessageBox.question(
                self.view,
                "Targets not found",
                f"{len(untargeted_files)} file(s) contain(s) none of the targets indicated."
                "They will be ignored. Proceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                all_files += untargeted_files
                self.files_to_process = all_files
                return True
            else:
                return False
        else:
            QMessageBox.critical(self.view, "No files found",
                                 "No files have been found using your exclusion and inclusion parameters.")
            return False
        
    def _init_progress_bar(self,):

        skiprow = 0
        if self.model.widgets_values['detection_behead_ckbox']:
            skiprow = int(self.model.widgets_values['detection_behead_edit'])

        example_dataframe = pd.read_csv(self.files_to_process[0], index_col=False, skiprows=skiprow)
        if self.model.widgets_values['detection_column_selection_ckbox']:
            n_columns = int(self.model.widgets_values['detection_column_selection_edit'])
        else:
            if self.model.widgets_values["detection_exception_column_edit"]:
                n_columns = int(
                    len([col for col in example_dataframe.columns if self.model.widgets_values["detection_exception_column_edit"] not in col]))
            else:
                n_columns = len(example_dataframe.columns)

        self.view.progress_bar.set_range(0, self._update_number_of_tasks(len(self.files_to_process), n_columns))
        self.view.progress_bar.set_value(0)
    
    def _update_number_of_tasks(self, n_file, n_col, ):
        """
        Calculates the total number of tasks to be processed based on the configuration and input parameters.

        This method calculates the total number of tasks that need to be completed, taking into account
        various flags and parameters set in the model. The total task count is used to drive the progress
        bar, indicating how many tasks remain to be processed.

        Parameters
        ----------
        n_file : int
            The number of files to process.

        n_col : int
            The number of columns to process per file.

        Returns
        -------
        int
            The total number of tasks to be completed.
        """
        
        mea = 1 if self.model.widgets_values['detection_behead_ckbox'] else 0
        electrodes = 1 if self.model.widgets_values["detection_column_selection_ckbox"] else 0
        
        concat_result = 1  # n_file #* n_sample
        
        sending_result = 1
        
        saving_dataset = 1
        
        file_level_tasks = mea + electrodes # performed only once per file
        column_level_tasks = sending_result # performed once per column (multiple times per sample)
        
        total_tasks = 0
        total_tasks += (n_file * file_level_tasks
                        + n_file * n_col * column_level_tasks)
        # total_tasks = n_file
        
        print("total tasks:", file_level_tasks, column_level_tasks, total_tasks)
        # total_tasks = n_file if not make_dataset else n_file + 1
        return total_tasks
    
    def start_detection(self):
        if self.check_parameters():
            self.model.update_tableEditors()
            
            self._init_dataframe()
            if not self._select_files():
                return
            
            reply = QMessageBox.question(
                self.view,
                "Files found",
                f"{len(self.files_to_process)} files have been found.\nProceed with the spike detection ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return
            
            self.view.progress_bar.set_task("Initializing progress bar...")
            
            self._init_progress_bar()
            
            self.view.progress_bar.set_task("Spike detection...")
            
            self.view.progress_bar.canceled.connect(self.handle_cancel)
            
            self.files_queue = multiprocessing.Queue()
            
            # Populate the queue with files
            for file in self.files_to_process:
                self.files_queue.put(file)
            
            # Add sentinel values (one per worker)
            for _ in range(1):
                self.files_queue.put(None)
                
            self.processing_thread = SpikeDetectorProcess(self.files_queue, self.model.widgets_values, self.model.targets)
            
            # Connect signals to slots
            self.processing_thread.result_ready.connect(self.handle_result)
            self.processing_thread.progress_made.connect(self.handle_progress)
            self.processing_thread.error_occurred.connect(self.handle_error)
            self.processing_thread.finished.connect(self.handle_finished)
            self.processing_thread.cancelled.connect(self.handle_cancel)
            
            # Start the worker thread
            self.processing_thread.start()
            self.app.add_thread("SpikeDetector", self.processing_thread)
            
    def _init_dataframe(self):
        unit = self.model.widgets_values["detection_unit_edit"]
        if not unit:
            unit = "AU"
        headers = [h.replace("###", unit) for h in self.result_headers]
        self.result_headers = headers
        self.resulting_dataframe = pd.DataFrame(columns=self.result_headers, )
        
    def handle_result(self, dataset):
        
        # dataset_row = [file, target, column_id, i, peak_value, peak_value_index, min_value,
        #                max_value, slope, peaks_ratio, shifted_min_index, shifted_max_index, shifted_extracted_spike]
        
        length = 10
        characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
        random_string = ''.join(random.choices(characters, k=length))
        while random_string in self.all_random_keys:
            random_string = ''.join(random.choices(characters, k=length))
        
        dataset.insert(0, random_string)
        self.all_random_keys.append(random_string)
        self.resulting_dataframe.loc[len(self.resulting_dataframe)] = dataset
    
    def handle_cancel(self):
        """Handle cancel button click."""
        self.processing_thread.stop()
        self.processing_thread.wait()
        self.results = {}
        self.all_random_keys = []
        self.view.progress_bar.reset()
        self.resulting_dataframe = pd.DataFrame(columns=self.result_headers, )
        
    def handle_progress(self, count):
        self.view.progress_bar.increment_steps(count)
        # Update progress bar, etc.
    
    def handle_error(self, worker_name, error_msg):
        logger.error(f"Error from {worker_name}: {error_msg}")
        self.processing_thread.stop()
        self.processing_thread.wait()
        self.results = {}
        self.all_random_keys = []
        self.view.progress_bar.reset()
        self.resulting_dataframe = pd.DataFrame(columns=self.result_headers, )
        # Show error dialog, log, etc.
    
    def handle_finished(self, worker_name,):
        logger.info(f"Worker {worker_name} finished processing.")
        pass
        
        processing_time_end = datetime.datetime.now()
        self.view.progress_bar.set_task("Saving dataframe...")
        self.resulting_dataframe.to_csv(self.model.widgets_values["detection_save_edit"], index=False)
        logger.info(f"Processing time: {processing_time_end - self.processing_time_start}")

        QMessageBox.information(self.view, "Detection finished", "Spike detection dataset successfully saved.")
        self.view.progress_bar.set_task("No task running.")
        self.view.progress_bar.reset()
    
    def load_model(self):
        model_path = \
            QFileDialog.getOpenFileName(parent=self.view, caption="Loading spike detection configuration", directory=".",
                                        filter="*" + self.model.extension)[0]
        if model_path:
            self.model.load_model(path=model_path)
            self.parent_controller.parent_controller.update_view_from_model(self.view, self.model)
    
    def save_model(self):
        self.parent_controller.parent_controller.update_model_from_view(self.model, self.view)
        model_path = \
            QFileDialog.getSaveFileName(parent=self.view, caption="Save spike detection configuration", directory=".",
                                        filter="*" + self.model.extension)[0]
        if model_path:
            self.model.save_model(path=model_path)
