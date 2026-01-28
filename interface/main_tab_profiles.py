from PyQt6.QtWidgets import (QTabWidget, QVBoxLayout)

from interface.translatable_widget import TranslatableWidget
from interface.tab_profile_create import TabProfileCreate
from interface.tab_profile_view import TabProfileView

class MainTabProfiles(TranslatableWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.tab_profile_create = TabProfileCreate()
        self.tab_profile_view = TabProfileView()

        self.tabs.addTab(self.tab_profile_create, self.tr("Create Profile"))
        self.tabs.addTab(self.tab_profile_view, self.tr("View Profile"))
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)