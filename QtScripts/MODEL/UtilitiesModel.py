from QtScripts import params as params


class UtilitiesModel:
    def __init__(self, controller):
        self.version = params.version
        self.controller = controller
        
        self.rename_targets = {}
        self.widgets_values = {}
        
    def update_tableEditors(self):
        self.rename_targets = {}
        for key, value in self.widgets_values["rename_tableedit"]:
            self.rename_targets[key] = value