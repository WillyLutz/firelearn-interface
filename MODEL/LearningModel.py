from data import params


class LearningModel:

    def __init__(self, main_model):
        self.main_model = main_model
        self.version = self.main_model.version
        self.__dataset_path = ""
        self.__save_rfc_directory = ""
        self.__rfc = None
        self.__entries_params = {}
        self.__switches_params = {}
        self.__cboxes_params = {}
        self.__strvar_params = {}

    @property
    def dataset_path(self):
        return self.__dataset_path

    @dataset_path.setter
    def dataset_path(self, value):
        self.__dataset_path = value

    @property
    def cboxes_params(self):
        return self.__cboxes_params

    @cboxes_params.setter
    def cboxes_params(self, value):
        self.__cboxes_params = value

    @property
    def save_rfc_directory(self):
        return self.__save_rfc_directory

    @save_rfc_directory.setter
    def save_rfc_directory(self, value):
        self.__save_rfc_directory = value

    @property
    def entries_params(self):
        return self.__entries_params

    @entries_params.setter
    def entries_params(self, value):
        self.__entries_params = value

    @property
    def rfc(self):
        return self.__rfc

    @rfc.setter
    def rfc(self, value):
        self.__rfc = value

    @property
    def switches_params(self):
        return self.__switches_params

    @switches_params.setter
    def switches_params(self, value):
        self.__switches_params = value

    @property
    def strvar_params(self):
        return self.__strvar_params

    @strvar_params.setter
    def strvar_params(self, value):
        self.__strvar_params = value

    def load_model(self, path):
        # todo : load model
        pass

    def save_model(self, path):
        # todo : save model
        pass