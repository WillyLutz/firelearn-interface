from multiprocessing import Process

import numpy as np


class SpikeDetectorProcess(Process):
    def __init__(self, df, columns, threshold, sf, dead_window, return_dict, queue, **kwargs):
        super().__init__(**kwargs)
        self.columns = columns
        self.threshold = threshold
        self.sf = sf
        self.dead_window = dead_window
        
        self.data = df
        self.queue = queue
        
        self.detected_spikes = return_dict
    
    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self.detected_spikes
    
    def run(self):
        # self.data = np.array(pd.read_csv(self.filename, skiprows=6, dtype=np.float64, usecols=self.columns))
        dead_samples = int(self.dead_window * self.sf)  # Dead time in number of samples
        
        for i_col in range(0, self.data.shape[1]):
            col_array = self.data[:, i_col]
            
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
                    if col_array[i] <= -self.threshold * std or col_array[i] >= self.threshold * std:
                        detected_indices.append(i)  # Record the spike index
                        i += dead_samples  # Skip the dead time window
                    else:
                        i += 1  # Move to the next index
                
                if len(detected_indices) > 0:
                    self.detected_spikes[self.columns[i_col]] = len(detected_indices)
                else:
                    self.detected_spikes[self.columns[i_col]] = 0
            
            self.queue.put(1)

