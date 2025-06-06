from PyQt6.QtWidgets import QComboBox
from PyQt6.QtGui import QWheelEvent

class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event: QWheelEvent):
        event.ignore()
