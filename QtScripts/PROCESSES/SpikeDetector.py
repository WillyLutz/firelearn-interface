import numpy as np
import pandas as pd
from PyQt6.QtCore import QThread, pyqtSignal

from QtScripts.CONTROLLER import data_processing
import logging
import json
logger = logging.getLogger("__SpikeDetector__")
class SpikeDetectorProcess(QThread):
    result_ready = pyqtSignal(object)
    progress_made = pyqtSignal(int)
    finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str, str)
    cancelled = pyqtSignal()
    def __init__(self, files_queue, model_values, targets, **kwargs):
        super().__init__(**kwargs)
        self.model_values = model_values
        self.files_queue = files_queue
        self.targets = targets
        self.files_queue = files_queue
        self._stop_flag = False
        self.has_error_occurred = False
        
    def stop(self):
        self._stop_flag = True


    def run(self):
        while not self._stop_flag:
            try:
                if self.files_queue.empty():
                    break
                
                file = self.files_queue.get_nowait()
                
                if file is None:
                    break
                
                if self._stop_flag:
                    break
                    
                self._file_spike_detection(file, )
                
                if self._stop_flag:
                    break
                
                self.progress_made.emit(1)
                
                logger.info(f"Worker {self.objectName()} processed file: {file}")
            
            except Exception as e:
                logger.exception(f"Worker {self.objectName()} encountered an error.")
                self.error_occurred.emit(self.objectName(), str(e))
                self.has_error_occurred = True
                break
        
        if not self.has_error_occurred:
            if self._stop_flag:
                self.cancelled.emit()
            else:
                self.finished.emit(self.objectName())

    def _file_spike_detection(self, file):
        logger.debug(f"detecting file {file}")
        target = ""
        for t, v in self.targets.items():
            if t in file:
                target = v
        if self._stop_flag: return None
        
        if self.model_values["detection_behead_ckbox"]:
            df = pd.read_csv(file, skiprows=int(self.model_values["detection_behead_edit"]), dtype=float, index_col=False,)
        else:
            df = pd.read_csv(file, dtype=float, index_col=False, )
            
        if not self.model_values["detection_exception_column_edit"]:
            columns_with_exception = df.columns
        else:
            columns_with_exception = [col for col in df.columns if self.model_values["detection_exception_column_edit"] not in col]
        
        df = df.loc[:, columns_with_exception]

        if self._stop_flag: return None
        if self.model_values["detection_column_selection_ckbox"]:
            df = data_processing.top_n_columns(df, int(self.model_values["detection_column_selection_edit"]))
            
        # columns_with_exception = [col for col in df.columns if self.model_vars["except column"] not in col]

        # self.data = np.array(pd.read_csv(self.filename, skiprows=6, dtype=np.float64, usecols=self.columns))
        

        data = df.values
        if self._stop_flag: return None
        
        for i_col in range(0, data.shape[1]):
            if self._stop_flag: return None
            
            col_array = data[:, i_col]
            self._column_spike_detection(col_array, file, target, df.columns[i_col])
        return None
    
    def _column_spike_detection(self, col_array, file, target, column_id):
        if file == "/media/wlutz/TOSHIBA EXT/Electrical activity analysis/EV_GW/DATA/P39102_GW_EV/P39102_DisabledFlow_GW_EV_T=10_M=30_Analog.csv":
            pass
        sf = int(self.model_values["detection_sampling_frequency_edit"])
        dead_window = float(self.model_values["detection_dead_window_edit"])
        threshold = float(self.model_values["detection_threshold_edit"])
        dead_samples = int(dead_window * sf)  # Dead time in number of samples
        min_margin = int(float(self.model_values[
                                   "detection_extraction_min_margin_edit"]) * sf)  # low extraction margin in number of points
        max_margin = int(float(self.model_values[
                                   "detection_extraction_max_margin_edit"]) * sf)  # high extraction margin in number of points
        on_edge_behavior = self.model_values["detection_on_edge_cbbox"]
        
        if np.any(col_array):
            row = 0
            std = col_array.std()
            # indices = np.where((-thresh*std >= col_array) | (col_array >= thresh*std))[0]
            # logger.info(indices)
            i = 0
            skipped_i = i
            for i in range(len(col_array)):
                if skipped_i > i:
                    continue
                # Check if the value is above or below the threshold
                if col_array[i] <= -threshold * std or col_array[i] >= threshold * std:
                    low_index = i - min_margin
                    high_index = i + max_margin
                    
                    if low_index >= 0 and high_index < len(col_array): # margins exist
                        pass
                    else: # One of the margins is out of bound
                        if on_edge_behavior == "Ignore":
                            logger.debug("Spike ignored")
                            continue
                        elif on_edge_behavior == "Include trimmed":
                            low_index = 0 if low_index < 0 else low_index
                            high_index = len(col_array) - 1 if high_index > len(col_array) else high_index
                            logger.debug(f"Spike trimmed")
                    
                    if col_array[i] >= threshold * std:
                        peak_value_index = np.argmax(col_array[low_index:high_index]) + low_index # indices in column referential
                    else:
                        peak_value_index = np.argmin(col_array[low_index:high_index]) + low_index # indices in column referential
                        
                    absolute_peak_index = np.argmax(np.abs(col_array[low_index:high_index])) + low_index
                    
                    # the spike is considered to be the maximum value in the [min_margin:max_margin] window
                    shifted_low_index = peak_value_index - min_margin
                    shifted_high_index = peak_value_index + max_margin
                    
                    if shifted_low_index >= 0 and shifted_high_index < len(col_array):  # margins exist
                        pass
                    else:  # One of the margins is out of bound
                        if on_edge_behavior == "Ignore":
                            logger.debug("Shifted spike ignored")
                            continue
                        elif on_edge_behavior == "Include trimmed":
                            shifted_low_index = 0 if shifted_low_index < 0 else shifted_low_index
                            shifted_high_index = len(col_array) - 1 if shifted_high_index > len(col_array) else shifted_high_index
                            logger.debug(f"Shifted spike trimmed")
                            
                    shifted_extracted_spike = col_array[shifted_low_index:shifted_high_index]
                    
                    peak_value = col_array[peak_value_index]
                    absolute_peak_value =  col_array[absolute_peak_index]
                    shifted_min_index = np.argmin(shifted_extracted_spike)
                    shifted_max_index = np.argmax(shifted_extracted_spike)
                    min_value = shifted_extracted_spike[shifted_min_index]
                    max_value = shifted_extracted_spike[shifted_max_index]
                    
                    if absolute_peak_index != i:
                        slope = (absolute_peak_value - col_array[i]) / (absolute_peak_index - i)
                    else:
                        slope = "Uncomputable"
                    peaks_ratio = np.abs(min_value - std) / np.abs(max_value - std)
                    
                    json_data = json.dumps(shifted_extracted_spike.tolist())
                    dataset_row = [file, sf, len(col_array), target, column_id, i, peak_value, peak_value_index, min_value,
                                   max_value, slope, peaks_ratio, shifted_low_index, shifted_high_index, json_data]
                    
                    self.result_ready.emit(dataset_row)
                    i_shift = shifted_high_index - high_index
                    skipped_i += dead_samples + i_shift  # Skip the dead time window
                else:
                    skipped_i += 1  # Move to the next index
            
            else:
                pass
                # self.detected_spikes[self.columns[i_col]].append(0)
        if self._stop_flag: return None
        
        self.progress_made.emit(1)
        return None