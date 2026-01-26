from PyQt6.QtWidgets import QTabWidget, QVBoxLayout
from interface.translatable_widget import TranslatableWidget
from interface.AbaColetarDados import AbaColetarDados
from interface.AbaPerfilColeta import AbaPerfilColeta

class MainTabCollection(TranslatableWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.tab_collect_data = AbaColetarDados()
        self.tab_create_profile = AbaPerfilColeta()

        self.tabs.addTab(self.tab_collect_data, self.tr("Collect Data"))
        self.tabs.addTab(self.tab_create_profile, self.tr("Create Profile"))
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)