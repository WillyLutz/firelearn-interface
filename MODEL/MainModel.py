import data.params as params
import pandas as pd
class Model:
    def __init__(self):
        self.__loaded_dataset_path = params.default_dataset_path
        self.__loaded_dataset = pd.DataFrame
        self.__selected_target = params.selected_target

    def set_loaded_dataset_path(self, ds):
        self.__loaded_dataset_path = ds

    def get_loaded_dataset_path(self):
        return self.__loaded_dataset_path
    
    def set_selected_target(self, target):
        self.__selected_target = target

    def get_selected_target(self):
        return self.__selected_target

    def set_loaded_dataset(self, dataset):
        self.__loaded_dataset = dataset

    def get_loaded_dataset(self):
        return self.__loaded_dataset
