from QtScripts import params


class ConfusionModel:
    def __init__(self, controller):
        self.controller = controller
        self.version = params.version
        self.widgets_values = {}
        self.full_dataset = None
        self.classifier = None
        self.train_targets = []
        self.test_targets = []