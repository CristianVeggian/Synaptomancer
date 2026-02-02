from PyQt6.QtWidgets import QVBoxLayout, QTabWidget

from interface.translatable_widget import TranslatableWidget
from interface.tab_protocol_motor_imagery import TabProtocolMotorImagery
from interface.tab_protocol_emg import TabProtocolEMG
from interface.tab_protocol_ecg import TabProtocolECG


class MainTabProtocols(TranslatableWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.tab_protocol_motor_imagery = TabProtocolMotorImagery()
        self.tab_protocol_emg = TabProtocolEMG()
        self.tab_protocol_ecg = TabProtocolECG()

        self.tabs.addTab(
            self.tab_protocol_motor_imagery,
            "🧠 " + self.tr("Create Motor Imagery Protocol"),
        )
        self.tabs.addTab(self.tab_protocol_ecg, "❤️ " + self.tr("Create ECG Protocol"))
        self.tabs.addTab(self.tab_protocol_emg, "💪 " + self.tr("Create EMG Protocol"))
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
