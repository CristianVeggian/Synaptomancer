from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QTabWidget, QVBoxLayout

from interface.window_settings import SettingsDialog
from interface.translatable_widget import TranslatableWidget
from interface.main_tab_acquisition import MainTabAcquisition
from interface.main_tab_pipeline import MainTabPipeline
from interface.main_tab_plugins import MainTabPlugins
from interface.main_tab_profiles import MainTabProfiles
from interface.main_tab_protocols import MainTabProtocols

class MainWindow(TranslatableWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synaptomancer")
        self.resize(800, 600)

        layout_principal = QVBoxLayout()

        self.abas = QTabWidget()

        self.main_tab_acquisition = MainTabAcquisition()
        self.main_tab_profiles = MainTabProfiles()
        self.main_tab_protocols = MainTabProtocols()
        self.main_tab_processing = MainTabPipeline()
        self.main_tab_plugins = MainTabPlugins()

        self.abas.addTab(self.main_tab_acquisition, self.tr("Data"))
        self.abas.addTab(self.main_tab_profiles, self.tr("Profiles"))
        self.abas.addTab(self.main_tab_protocols, self.tr("Protocols"))
        self.abas.addTab(self.main_tab_processing, self.tr("Processing"))
        self.abas.addTab(self.main_tab_plugins, self.tr("Plugins"))

        layout_principal.addWidget(self.abas)
        self.setLayout(layout_principal)
        self.showMaximized()

        self._setup_shortcuts()

    def _setup_shortcuts(self):
        shortcut_settings = QShortcut(
            QKeySequence("Ctrl+."),
            self
        )
        shortcut_settings.activated.connect(self.open_settings)

    def open_settings(self):
        if not hasattr(self, "settings_dialog"):
            self.settings_dialog = SettingsDialog(self)

        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
