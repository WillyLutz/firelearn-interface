from multiprocessing import Process

import numpy as np
import pandas as pd

from scripts.CONTROLLER import data_processing


class SpikeDetectorProcess(Process):
    def __init__(self, model_vars, model_targets, n_cols, result_queue, files_queue, progress_queue, **kwargs):
        super().__init__(**kwargs)
        
        self.model_vars = model_vars
        self.progress_queue = progress_queue
        self.n_cols = n_cols
        self.files_queue = files_queue
        self.result_queue = result_queue
        self.model_targets = model_targets
        
    
    
    def run(self):
        self._detection_for_worker()
        self.result_queue.put((self.name, 0), timeout=10)
        print(f"Worker {self.name} has exited")

    def _detection_for_worker(self):

        while True:
            print("spike detection process progress queue size", self.progress_queue.qsize())

            try:
                file = self.files_queue.get(timeout=1)
                # check for sentinel value
                if file is None:
                    print(f"Worker {self.name} received stop signal and is exiting gracefully.")
                    break
                    
                result = self._spike_detection(file)
                target = None
                
                for t, v in self.model_targets.items():
                    if v in file:
                        target = v
                    
                if self.result_queue.full():
                    print(f"Worker {self.name} encountered an error adding results of {file}:")

                self.result_queue.put((result, target), timeout=10)
                self.progress_queue.put(1)
                print(f"Worker {self.name} DONE - file queue size: {self.files_queue.qsize()}")
            except Exception as e:
                print(f"Worker {self.name} encountered an error. Terminating. {e}")
                break
        print(f"Worker {self.name} exiting. Final files queue size: {self.files_queue.qsize()}")

    
    def _spike_detection(self, file):
        sf = int(self.model_vars["sampling frequency"])
        dead_window = float(self.model_vars["dead window"])
        threshold = float(self.model_vars["std threshold"])
        
        
        if self.model_vars["behead ckbox"]:
            df = pd.read_csv(file, skiprows=int(self.model_vars["behead"]), dtype=float, index_col=False)
        else:
            df = pd.read_csv(file, dtype=float, index_col=False)
        
        if self.model_vars["select columns ckbox"]:
            df = data_processing.top_n_columns(df, self.n_cols, self.model_vars["except column"])
        
        columns_with_exception = [col for col in df.columns if self.model_vars["except column"] not in col]
        detected_spikes = {col: [] for col in columns_with_exception}

        # self.data = np.array(pd.read_csv(self.filename, skiprows=6, dtype=np.float64, usecols=self.columns))
        dead_samples = int(dead_window * sf)  # Dead time in number of samples
        
        data = df.loc[:, columns_with_exception].values

        for i_col in range(0, data.shape[1]):
            col_array = data[:, i_col]
            
            all_workers = []
            if np.any(col_array):
                row = 0
                std = col_array.std()
                # indices = np.where((-thresh*std >= col_array) | (col_array >= thresh*std))[0]
                # print(indices)
                detected_indices = []
                i = 0
                
                while i < len(col_array):
                    # Check if the value is above or below the threshold
                    if col_array[i] <= -threshold * std or col_array[i] >= threshold * std:
                        detected_indices.append(i)  # Record the spike index
                        i += dead_samples  # Skip the dead time window
                    else:
                        i += 1  # Move to the next index
                
                if len(detected_indices) > 0:
                    for d in detected_indices:
                        detected_spikes[df.columns[i_col]].append(d)
                else:
                    pass
                    # self.detected_spikes[self.columns[i_col]].append(0)
            
            self.progress_queue.put(1)
            
        return detected_spikes
