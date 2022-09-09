class Model:
    def __init__(self):
        self.__loaded_dataset = None

    def set_loaded_dataset(self, ds):
        self.__loaded_dataset = ds

    def get_loaded_dataset(self):
        return self.__loaded_dataset
