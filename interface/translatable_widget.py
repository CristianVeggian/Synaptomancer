from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QCoreApplication

class TranslatableWidget(QWidget):
    def tr(self, text: str) -> str:
        return QCoreApplication.translate(self.__class__.__name__, text)
