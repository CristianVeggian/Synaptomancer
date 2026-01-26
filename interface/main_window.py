from PyQt6.QtWidgets import QTabWidget, QVBoxLayout
from interface.translatable_widget import TranslatableWidget
from interface.main_tab_collection import MainTabCollection
from interface.main_tab_pipeline import MainTabPipeline
from interface.main_tab_plugins import MainTabPlugins

class MainWindow(TranslatableWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synaptomancer")
        self.resize(800, 600)

        layout_principal = QVBoxLayout()

        # Criar o widget de abas
        self.abas = QTabWidget()

        # Criar abas individuais
        self.main_tab_collection = MainTabCollection()
        self.main_tab_pipeline = MainTabPipeline()
        self.main_tab_plugins = MainTabPlugins()

        # Adiciona as abas ao widget
        self.abas.addTab(self.main_tab_collection, self.tr("Collect Data"))
        self.abas.addTab(self.main_tab_pipeline, self.tr("Processing"))
        self.abas.addTab(self.main_tab_plugins, self.tr("Plugins"))

        # Adiciona o QTabWidget ao layout principal
        layout_principal.addWidget(self.abas)
        self.setLayout(layout_principal)
        self.showMaximized()