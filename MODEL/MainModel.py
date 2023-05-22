import data.params as params
import pandas as pd
class MainModel:
    def __init__(self):
        self.__parent_directory = ""
        self.__to_include = []
        self.__to_exclude = []

    @property
    def to_exclude(self):
        return self.__to_exclude

    @to_exclude.setter
    def to_exclude(self, value):
        self.__to_exclude = value

    @property
    def to_include(self):
        return self.__to_include

    @to_include.setter
    def to_include(self, value):
        self.__to_include = value

    @property
    def parent_directory(self):
        return self.__parent_directory

    @parent_directory.setter
    def parent_directory(self, value):
        self.__parent_directory = value
