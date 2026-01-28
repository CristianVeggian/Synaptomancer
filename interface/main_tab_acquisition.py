from PyQt6.QtWidgets import QTabWidget, QVBoxLayout
from interface.translatable_widget import TranslatableWidget
from interface.tab_acquisition_motor_imagery_data import TabAcquireMotorImageryData

class MainTabAcquisition(TranslatableWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.tab_collect_data = TabAcquireMotorImageryData()

        self.tabs.addTab(self.tab_collect_data, self.tr("Collect Motor Imagery Data"))
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)