from scripts.MODEL.AnalysisModel import AnalysisModel

class AnalysisController:
    """
    Controller class for handling interactions between the view and the AnalysisModel.

    Attributes:
        model (AnalysisModel): The data processing model.
        view: The UI component that interacts with the user.
        progress: Placeholder for progress tracking (not yet implemented).
    """

    def __init__(self, view):
        """
        Initializes the AnalysisController.

        Args:
            view: The UI component that interacts with the controller.
        """
        self.model = AnalysisModel()  # Instantiate the model
        self.view = view
        self.view.controller = self  # Link the controller to the view

        self.progress = None  # Placeholder for tracking progress
