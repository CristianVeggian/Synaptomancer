from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QLabel

class ToastMessage:
    def __init__(self, parent, texto, color='#28a745', duracao=2000):
        self.toast = QLabel(texto)  # Sem parent
        self.toast.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        self.toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toast.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.ToolTip |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.toast.adjustSize()

        # Centraliza na tela, relativo ao parent (posição global)
        parent_pos = parent.mapToGlobal(parent.rect().center())
        x = parent_pos.x() - self.toast.width() // 2
        y = parent_pos.y() - self.toast.height() // 2
        self.toast.move(x, y)

        self.toast.show()
        QTimer.singleShot(duracao, self.toast.close)