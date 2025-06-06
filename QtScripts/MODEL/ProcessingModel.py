from QtScripts import params as params


class ProcessingModel:
    def __init__(self, controller):
        self.version = params.version
        self.controller = controller
