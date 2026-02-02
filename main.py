from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale, QSettings

import sys

from functions.utils.mkdatadir import mkdatadir
from interface.window_main import MainWindow

if __name__ == "__main__":
    translator = QTranslator()

    settings = QSettings("Synaptomancer", "SynaptomancerApp")

    language = settings.value("language", QLocale.system().name())

    save_state = settings.value("save_state", True, bool)

    mkdatadir()
    app = QApplication(sys.argv)

    if translator.load(f"synapto_{language}", "translations/"):
        app.installTranslator(translator)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
