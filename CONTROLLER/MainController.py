class Controller:
    def __init__(self, model, view):
        self.view = view
        self.model = model

    def print_pressed(self):
        if self.model.pressed():
            print("pressed")