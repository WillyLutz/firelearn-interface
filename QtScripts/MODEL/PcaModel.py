from QtScripts import params


class PcaModel:
    def __init__(self, controller):
        self.controller = controller
        self.version = params.version
        self.widgets_values = {}
        self.dataset = None