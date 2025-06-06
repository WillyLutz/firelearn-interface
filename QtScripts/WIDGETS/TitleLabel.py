from PyQt6.QtWidgets import QLabel


class TitleLabel(QLabel):
    def __init__(self, parent=None, section='title1', **kwargs):
        super().__init__(parent, **kwargs)
        self.section = section
        self._apply_style()

    def _apply_style(self):
        match self.section:
            case 'title1':
                self.setObjectName("TitleLabel1")
            case 'title2':
                self.setObjectName("TitleLabel2")
        # Let the application-wide style sheet apply the correct style
