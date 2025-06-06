from QtScripts import params as params


class SpikeAnalysisModel:
    def __init__(self, controller):
        self.version = params.version
        self.controller = controller
        
        self.widgets_values = {}
        self.dataset = None
        
        self.dataset_base_columns = ["Key", "File", "Sampling frequency", "Number of values", "Target", "Column ID",
                               "Threshold crossing index", "Peak value", "Peak index",
                               "Minimum value", "Maximum value", "Slope", "Extrema ratio (min/max)",
                               "Extraction first index", "Extraction last index", "Extracted data",]