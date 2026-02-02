from PyQt6.QtWidgets import QTabWidget, QVBoxLayout
from interface.translatable_widget import TranslatableWidget
from interface.tab_acquisition_motor_imagery import TabAcquireMotorImageryData
from interface.tab_acquisition_ecg import TabAcquireECGData
from interface.tab_acquisition_emg import TabAcquireEMGData

class MainTabAcquisition(TranslatableWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.tab_collect_motor_imagery_data = TabAcquireMotorImageryData()
        self.tab_collect_ecg_data = TabAcquireECGData()
        self.tab_collect_emg_data = TabAcquireEMGData()

        self.tabs.addTab(self.tab_collect_motor_imagery_data, "🧠 " + self.tr("Collect Motor Imagery Data"))
        self.tabs.addTab(self.tab_collect_ecg_data, "❤️ " + self.tr("Collect ECG Data"))
        self.tabs.addTab(self.tab_collect_emg_data, "💪 " + self.tr("Collect EMG Data"))

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)