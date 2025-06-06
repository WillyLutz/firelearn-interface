from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal


class CustomProgressBar(QWidget):
    # Signal emitted when the cancel button is clicked
    canceled = pyqtSignal()

    def __init__(self, parent=None, task=""):
        super().__init__(parent)

        self.task = task
        self.steps = 0
        # Task label on the left
        self.label = QLabel(self.task)
        self.label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # Progress bar in the middle
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)

        # Cancel button on the right
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)

        # Horizontal layout
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def set_task(self, task: str):
        """Update the task label."""
        self.task = task
        self.label.setText(self.task)
        self.update()
        
    def set_value(self, value):
        self.progress_bar.setValue(value)

    def increment_steps(self, value: int):
        """Set progress bar value (0–100)."""
        self.steps += value
        self.progress_bar.setValue(self.steps)

    def set_maximum(self, max_val: int):
        self.progress_bar.setMaximum(max_val)

    def set_minimum(self, min_val: int):
        self.progress_bar.setMinimum(min_val)

    def reset(self):
        self.progress_bar.reset()
        self.progress_bar.update()
        self.steps = 0
        self.set_task("No task running.")

    def _on_cancel(self):
        """Handle cancel button click."""
        self.canceled.emit()

    def set_range(self, minimum, maximum):
        self.set_minimum(minimum)
        self.set_maximum(maximum)