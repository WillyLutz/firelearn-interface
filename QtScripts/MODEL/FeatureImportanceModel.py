from QtScripts import params


class FeatureImportanceModel:
    def __init__(self, controller):
        self.controller = controller
        self.version = params.version
        
        self.widgets_values = {}
        self.classifier = None