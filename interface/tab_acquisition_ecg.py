import json
import numpy as np

import pyqtgraph as pg
from serial.tools.list_ports import comports
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFileDialog,
    QSizePolicy,
    QFormLayout,
    QHBoxLayout,
    QRadioButton,
    QGroupBox,
)
from PyQt6.QtWidgets import QButtonGroup

from interface.components.toast_message import ToastMessage
from functions.acquisition_worker_ecg import AcquisitionWorkerECG
from functions.utils.paths import PROFILES_DIR, PROTOCOLS_DIR
from functions.utils.color import ERROR_COLOR, SUCCESS_COLOR


class TabAcquireECGData(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()

        self.form_layout = QFormLayout()

        self.line_edit_profile = QLineEdit()
        self.line_edit_profile.setPlaceholderText(self.tr("Select profile file..."))
        self.line_edit_profile.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.btn_browse_profile = QPushButton(self.tr("Browse"))
        self.btn_browse_profile.clicked.connect(self._browse_profile)

        profile_field_layout = QHBoxLayout()
        profile_field_layout.addWidget(self.line_edit_profile)
        profile_field_layout.addWidget(self.btn_browse_profile)

        self.form_layout.addRow(QLabel(self.tr("Profile")), profile_field_layout)

        self.line_edit_protocol = QLineEdit()
        self.line_edit_protocol.setPlaceholderText(self.tr("Select protocol file..."))
        self.line_edit_protocol.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.btn_browse_protocol = QPushButton(self.tr("Browse"))
        self.btn_browse_protocol.clicked.connect(self._browse_protocol)

        protocol_field_layout = QHBoxLayout()
        protocol_field_layout.addWidget(self.line_edit_protocol)
        protocol_field_layout.addWidget(self.btn_browse_protocol)

        self.form_layout.addRow(QLabel(self.tr("Protocol")), protocol_field_layout)

        self.combo_serial = QComboBox()
        self.combo_serial.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        self.btn_serial_refresh = QPushButton(self.tr("Refresh"))
        self.btn_serial_refresh.setToolTip(self.tr("Refresh serial ports"))
        self.btn_serial_refresh.clicked.connect(self._refresh_ports)

        serial_layout = QHBoxLayout()
        serial_layout.addWidget(self.combo_serial)
        serial_layout.addWidget(self.btn_serial_refresh)

        self.form_layout.addRow(QLabel(self.tr("Serial Port")), serial_layout)

        self.main_layout.addLayout(self.form_layout)

        self.graphic = pg.GraphicsLayoutWidget()

        self.graphic_started = False

        self.radio_visualize = QRadioButton(self.tr("Visualize Only"))
        self.radio_save_data = QRadioButton(self.tr("Save Data"))

        self.radio_visualize.setChecked(True)

        modo_groupbox = QGroupBox(self.tr("Operation Mode"))
        modo_layout = QHBoxLayout()
        modo_layout.addWidget(self.radio_visualize)
        modo_layout.addWidget(self.radio_save_data)
        modo_groupbox.setLayout(modo_layout)

        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.radio_visualize, 0)
        self.mode_group.addButton(self.radio_save_data, 1)

        self.main_layout.addWidget(modo_groupbox)

        self.btn_start_acquisition = QPushButton(self.tr("Start acquisition"))
        self.btn_start_acquisition.clicked.connect(self._start_acquisition)

        self.main_layout.addWidget(self.btn_start_acquisition)
        self.main_layout.addStretch(1)

        bottom_layout = QHBoxLayout()

        bottom_layout.addWidget(self.graphic)
        self.main_layout.addLayout(bottom_layout)

        self._refresh_ports()
        self.setLayout(self.main_layout)

    def _refresh_ports(self):
        try:
            ports = [port.device for port in comports()]
            self.combo_serial.clear()
            if not ports:
                self.combo_serial.addItem(self.tr("No port"))
                self.combo_serial.setEnabled(False)
            else:
                self.combo_serial.addItems(ports)
                self.combo_serial.setEnabled(True)
        except Exception as e:
            self.toast = ToastMessage(
                self, self.tr("Error listing ports: {0}").format(str(e)), ERROR_COLOR
            )

    def _browse_profile(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Profile File"),
            PROFILES_DIR,
            "JSON Files (*.json);;All Files (*)",
        )
        if fileName:
            self.line_edit_profile.setText(fileName)

    def _browse_protocol(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select protocol File"),
            PROTOCOLS_DIR,
            "JSON Files (*.json);;All Files (*)",
        )
        if fileName:
            self.line_edit_protocol.setText(fileName)

    def _start_acquisition(self):
        profile_path = self.line_edit_profile.text()
        protocol_path = self.line_edit_protocol.text()

        if not profile_path:
            self.toast = ToastMessage(
                self, self.tr("Select a profile file"), ERROR_COLOR
            )
            return

        if not protocol_path:
            self.toast = ToastMessage(
                self, self.tr("Select a protocol file"), ERROR_COLOR
            )
            return

        params = {"serial_port": self.combo_serial.currentText(), "baud_rate": 115200}

        try:
            with open(protocol_path, "r") as f:
                self.protocol = json.load(f)
        except Exception as e:
            self.toast = ToastMessage(
                self, self.tr("Error loading protocol: {0}").format(str(e)), ERROR_COLOR
            )
            return

        self.toast = ToastMessage(
            self,
            self.tr("Starting acquisition with board {0}").format("ESP32"),
            "#0077cc",
        )

        if hasattr(self, "worker") and self.worker.isRunning():
            self.toast = ToastMessage(
                self, self.tr("Acquisition already running."), ERROR_COLOR
            )
            return

        self.btn_start_acquisition.setEnabled(False)
        self.combo_serial.setEnabled(False)
        self.line_edit_profile.setEnabled(False)
        self.btn_browse_profile.setEnabled(False)

        mode_id = self.mode_group.checkedId()

        self.worker = AcquisitionWorkerECG(
            params=params,
            protocol_path=protocol_path,
            profile_path=profile_path,
            mode=mode_id,
        )
        self.worker.sig_status.connect(self.status_controller)
        self.worker.sig_sampling_rate.connect(self._start_graphic)
        self.worker.sig_sample.connect(self._plot_sample)
        self.worker.start()

    def _restore_ui(self):
        self.btn_start_acquisition.setEnabled(True)
        self.combo_serial.setEnabled(True)
        self.line_edit_profile.setEnabled(True)
        self.btn_browse_profile.setEnabled(True)
        self.line_edit_protocol.setEnabled(True)
        self.btn_browse_protocol.setEnabled(True)

    def _start_graphic(self, sampling_rate):
        self.sampling_rate = sampling_rate

        self.channel_name = "ECG"

        self.window_size = 4
        self.num_points = sampling_rate * self.window_size

        self.buffer = np.zeros(self.num_points)
        self.timestamps = np.linspace(-self.window_size, 0, self.num_points)

        self.graphic.clear()
        self.graphic.setBackground("w")

        self.plot = self.graphic.addPlot(row=0, col=0)
        self.plot.setTitle(self.tr("Real Time ECG"))
        self.plot.setLabel("left", self.channel_name)
        self.plot.setLabel("bottom", self.tr("Time (s)"))

        self.curve = self.plot.plot(pen=pg.mkPen(color="b", width=1.5))

        self.graphic_started = True

    def _plot_sample(self, sample):
        if not self.graphic_started:
            return

        try:
            _, value = sample

            self.timestamps += 1 / self.sampling_rate

            self.buffer = np.roll(self.buffer, -1)
            self.buffer[-1] = value

            self.curve.setData(x=self.timestamps, y=self.buffer)

        except Exception as e:
            print("Erro ao plotar ECG:", e)

    def status_controller(self, status, code):
        if status == 1:
            self.toast = ToastMessage(
                self, self.tr("Acquisition started"), SUCCESS_COLOR
            )
        elif status == 2:
            self.toast = ToastMessage(
                self, self.tr("Acquisition completed"), SUCCESS_COLOR
            )
            self._restore_ui()
        elif status == -1:
            self.toast = ToastMessage(self, code, ERROR_COLOR)
            self._restore_ui()
