from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale, QLibraryInfo

import sys

from functions.utils.mkdatadir import mkdatadir
from interface.main_window import MainWindow

if __name__ == "__main__":

    translator = QTranslator()
    locale = QLocale.system().name()

    mkdatadir()
    app = QApplication(sys.argv)

    if translator.load(f"synapto_{locale}", "translations/"):
        app.installTranslator(translator)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())