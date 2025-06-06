from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QAbstractButton

from QtScripts.params import resource_path


class ImageButton(QAbstractButton):
    def __init__(self, pixmap:QPixmap=None, pixmap_path:str=None):
        super().__init__()
        if not pixmap:
            pixmap = QPixmap(resource_path(pixmap_path))
        elif not pixmap:
            raise ValueError("pixmap_path or pixmap must not be None")
        
        self.pixmap = pixmap
        self.pressed.connect(self.update)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)
    
    def sizeHint(self):
        return self.pixmap.size()
        