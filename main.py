from PyQt6.QtWidgets import QApplication
import sys

from interface.Janela import Janela

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setStyle("Fusion")
    janela = Janela()
    janela.show()
    sys.exit(app.exec())