import json
from os.path import join
from serial.tools.list_ports import comports
from interface.components.toast_message import ToastMessage
from functions.acquisition_worker_motor_imagery import AcquisitionWorkerMotorImagery
from brainflow import BrainFlowInputParams
from brainflow.board_shim import BoardIds
from PyQt6.QtWidgets import QButtonGroup
import threading

import numpy as np

from functions.utils.board_config import board_details
from functions.utils.beep import beep
from functions.utils.paths import ASSETS_DIR, PROFILES_DIR, PROTOCOLS_DIR
from functions.utils.color import ERROR_COLOR, SUCCESS_COLOR

import pyqtgraph as pg
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QIntValidator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFileDialog, QSizePolicy, QDoubleSpinBox,
    QFormLayout, QHBoxLayout, QRadioButton, QGroupBox

)

class TabAcquireMotorImageryData(QWidget):
    def __init__(self):
        super().__init__()

        self.active_event_name = "None"
        self.btn_serial = QPushButton()
        try:
            icon_path = join(ASSETS_DIR, 'refresh.png')
            if not QIcon(icon_path).isNull():
                self.btn_serial.setIcon(QIcon(icon_path))
            else:
                self.btn_serial.setText("↻")
        except Exception as e:
            self.btn_serial.setText("↻")

        self.btn_serial.setIconSize(QSize(20, 20))
        self.btn_serial.setToolTip(self.tr("Refresh serial ports"))
        self.btn_serial.setFixedSize(28, 28)
        self.btn_serial.clicked.connect(self._refresh_ports)

        self.label_placa = QLabel(self.tr("Board"))
        self.combo_boards = QComboBox()
        self.combo_boards.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_boards.addItems([board.name for board in BoardIds if board not in (BoardIds.STREAMING_BOARD, BoardIds.PLAYBACK_FILE_BOARD)])
        self.combo_boards.setCurrentIndex(0)

        self.label_profile = QLabel(self.tr("Profile"))
        self.line_edit_profile = QLineEdit()
        self.line_edit_profile.setPlaceholderText(self.tr("Select profile file..."))
        self.line_edit_profile.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_browse_profile = QPushButton(self.tr("Browse"))
        self.btn_browse_profile.clicked.connect(self._browse_profile)

        self.label_protocol = QLabel(self.tr("Protocol"))
        self.line_edit_protocol = QLineEdit()
        self.line_edit_protocol.setPlaceholderText(self.tr("Select protocol file..."))
        self.line_edit_protocol.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_browse_protocol = QPushButton(self.tr("Browse"))
        self.btn_browse_protocol.clicked.connect(self._browse_protocol)

        self.btn_start_acquisition = QPushButton(self.tr("Start acquisition"))
        self.btn_start_acquisition.clicked.connect(self._start_acquisition)

        self.label_serial = QLabel(self.tr("Port"))
        self.combo_serial = QComboBox()
        self.label_mac = QLabel(self.tr("MAC Address"))
        self.field_mac = QLineEdit()
        self.label_ip = QLabel(self.tr("IP Address"))
        self.field_ip = QLineEdit()
        self.label_port = QLabel(self.tr("Port"))
        self.field_port = QLineEdit()
        self.label_timeout = QLabel(self.tr("Timeout"))
        self.field_timeout = QDoubleSpinBox()

        self.combo_serial.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.field_mac.setPlaceholderText("xx:xx:xx:xx:xx:xx")
        self.field_port.setValidator(QIntValidator(1, 65535))
        self.field_port.setPlaceholderText(self.tr("Choose a WiFi port"))
        self.field_port.setText("6987")
        self.field_ip.setPlaceholderText("xxx.xxx.xxx.xxx")
        self.field_timeout.setValue(15)

        self.grafico = pg.GraphicsLayoutWidget()

        self.plots = []
        self.curvas = []
        self.buffers = {}
        self.grafico_inicializado = False

        main_layout = QVBoxLayout(self)

        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        form_layout.addWidget(self.label_placa, 0, 0, Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.combo_boards, 0, 1)
        form_layout.addWidget(self.label_profile, 1, 0, Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.line_edit_profile, 1, 1)
        form_layout.addWidget(self.btn_browse_profile, 1, 2)
        form_layout.addWidget(self.label_protocol, 2, 0, Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.line_edit_protocol, 2, 1)
        form_layout.addWidget(self.btn_browse_protocol, 2, 2)
        form_layout.setColumnStretch(1, 1)

        main_layout.addLayout(form_layout)

        self.campos_dinamicos_layout = QFormLayout()
        self.campos_dinamicos_widget = QWidget()
        self.campos_dinamicos_widget.setLayout(self.campos_dinamicos_layout)
        main_layout.addWidget(self.campos_dinamicos_widget)

        serial_layout = QHBoxLayout()
        serial_layout.addWidget(self.combo_serial)
        serial_layout.addWidget(self.btn_serial)
        self.campos_dinamicos_layout.addRow(self.label_serial, serial_layout)

        self.campos_dinamicos_layout.addRow(self.label_ip, self.field_ip)
        self.campos_dinamicos_layout.addRow(self.label_port, self.field_port)
        self.campos_dinamicos_layout.addRow(self.label_mac, self.field_mac)
        self.campos_dinamicos_layout.addRow(self.label_timeout, self.field_timeout)

        self.radio_visualize = QRadioButton(self.tr("Visualize Only"))
        self.radio_save_raw_data = QRadioButton(self.tr("Save Raw Data"))
        self.radio_save_filtered_data = QRadioButton(self.tr("Save Filtered Data"))

        self.radio_visualize.setChecked(True)

        modo_groupbox = QGroupBox(self.tr("Operation Mode"))
        modo_layout = QHBoxLayout()
        modo_layout.addWidget(self.radio_visualize)
        modo_layout.addWidget(self.radio_save_raw_data)
        modo_layout.addWidget(self.radio_save_filtered_data)
        modo_groupbox.setLayout(modo_layout)

        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.radio_visualize, 0)
        self.mode_group.addButton(self.radio_save_raw_data, 1)
        self.mode_group.addButton(self.radio_save_filtered_data, 2)

        main_layout.addWidget(modo_groupbox)

        main_layout.addWidget(self.btn_start_acquisition)
        main_layout.addStretch(1)

        bottom_layout = QHBoxLayout()
        feedback_layout = QVBoxLayout()

        self.btn_audio_feedback = QPushButton(self.tr("Activate audio feedback"))
        self.btn_audio_feedback.clicked.connect(self._control_audio_feedback)
        self.audio_feedback = False

        self.event_label = QLabel(self.tr("Waiting..."))
        self.event_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.event_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.event_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            border: 2px solid #ecf0f1;
            border-radius: 10px;
            padding: 20px;
        """)

        feedback_layout.addWidget(self.btn_audio_feedback)
        feedback_layout.addWidget(self.event_label)
        bottom_layout.addLayout(feedback_layout, stretch=3)
        bottom_layout.addWidget(self.grafico, stretch=7)
        main_layout.addLayout(bottom_layout)

        self.connection_types = board_details

        self._refresh_ports()
        self.combo_boards.currentTextChanged.connect(self._set_connection_interface)
        self._set_connection_interface(self.combo_boards.currentText())

    def _set_connection_interface(self, board_name):
        connection = self.connection_types.get(board_name, {})

        self.label_serial.hide()
        self.combo_serial.hide()
        self.btn_serial.hide()
        self.label_mac.hide()
        self.field_mac.hide()
        self.label_ip.hide()
        self.field_ip.hide()
        self.label_port.hide()
        self.field_port.hide()
        self.label_timeout.hide()
        self.field_timeout.hide()

        if 'serial' in connection:
            self.label_serial.show()
            self.combo_serial.show()
            self.btn_serial.show()
            self._refresh_ports()

        if 'mac' in connection:
            self.label_mac.show()
            self.field_mac.show()

        if 'ip_address' in connection:
            self.label_ip.show()
            self.field_ip.show()

        if 'port' in connection:
            self.label_port.show()
            self.field_port.show()

        if 'timeout' in connection:
            self.label_timeout.show()
            self.field_timeout.show()

        self.connection = connection

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
            self.toast = ToastMessage(self, self.tr("Error listing ports: {0}").format(str(e)), ERROR_COLOR)

    def _browse_profile(self):
        fileName, _ = QFileDialog.getOpenFileName(self,
                        self.tr("Select Profile File"),
                        PROFILES_DIR,
                        "JSON Files (*.json);;All Files (*)")
        if fileName:
            self.line_edit_profile.setText(fileName)

    def _browse_protocol(self):
        fileName, _ = QFileDialog.getOpenFileName(self,
                        self.tr("Select protocol File"),
                        PROTOCOLS_DIR,
                        "JSON Files (*.json);;All Files (*)")
        if fileName:
            self.line_edit_protocol.setText(fileName)

    def _start_acquisition(self):
        board_name = self.combo_boards.currentText()
        profile_path = self.line_edit_profile.text()
        protocol_path = self.line_edit_protocol.text()

        if not profile_path:
            self.toast = ToastMessage(
                self,
                self.tr("Select a profile file"),
                ERROR_COLOR
                )
            return
        
        if not protocol_path:
            self.toast = ToastMessage(
                self,
                self.tr("Select a protocol file"),
                ERROR_COLOR
                )
            return

        connection = self.connection_types.get(board_name, {})

        params = BrainFlowInputParams()

        if 'serial' in connection:
            serial = self.combo_serial.currentText()
            if connection['serial'] and not serial:
                self.toast = ToastMessage(self,
                                          self.tr("Select a serial port."),
                                          ERROR_COLOR)
                return
            params.serial_port = serial

        if 'mac' in connection:
            mac = self.field_mac.text().strip()
            if connection['mac'] and not mac:
                self.toast = ToastMessage(self, self.tr("Enter MAC address."), ERROR_COLOR)
                return
            params.mac_address = mac

        if 'ip_address' in connection:
            ip = self.field_ip.text().strip()
            if connection['ip'] and not ip:
                self.toast = ToastMessage(self, self.tr("Enter IP address."), ERROR_COLOR)
                return
            params.ip_address = ip

        if 'port' in connection:
            porta = self.field_port.text()
            if connection['port'] and not porta:
                self.toast = ToastMessage(self, self.tr("Enter port."), ERROR_COLOR)
                return
            params.ip_port = int(porta)

        if 'timeout' in connection:
            timeout = self.field_timeout.value()
            if connection['timeout'] and not timeout:
                self.toast = ToastMessage(self, self.tr("Set a timeout."), ERROR_COLOR)
                return
            params.timeout = timeout

        try:
            board_id = BoardIds[board_name].value
        except KeyError:
            self.toast = ToastMessage(self, self.tr("Invalid board name: {0}").format(board_name), ERROR_COLOR)
            return

        try:
            with open(protocol_path, 'r') as f:
                self.protocol = json.load(f)
        except Exception as e:
            self.toast = ToastMessage(self, self.tr("Error loading protocol: {0}").format(str(e)), ERROR_COLOR)
            return

        self.toast = ToastMessage(self, self.tr("Starting acquisition with board {0}").format(board_name), "#0077cc")

        if hasattr(self, 'worker') and self.worker.isRunning():
            self.toast = ToastMessage(self, self.tr("Acquisition already running."), ERROR_COLOR)
            return

        self.btn_start_acquisition.setEnabled(False)
        self.combo_serial.setEnabled(False)
        self.combo_boards.setEnabled(False)
        self.line_edit_profile.setEnabled(False)
        self.btn_browse_profile.setEnabled(False)

        mode_id = self.mode_group.checkedId()

        self.worker = AcquisitionWorkerMotorImagery(params=params, board_id=board_id, protocol_path=protocol_path, profile_path=profile_path, mode=mode_id)
        self.worker.sig_sampling_rate.connect(self._start_graphic)
        self.worker.sig_status.connect(self.status_controller)
        self.worker.sig_active_event.connect(self.get_evento_ativo)
        self.worker.sig_sample.connect(self._plot_sample)
        self.worker.start()

    def _restore_ui(self):
        self.btn_start_acquisition.setEnabled(True)
        self.combo_serial.setEnabled(True)
        self.combo_boards.setEnabled(True)
        self.line_edit_profile.setEnabled(True)
        self.btn_browse_profile.setEnabled(True)
        self.event_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            border: 2px solid #ecf0f1;
            border-radius: 10px;
            padding: 20px;
        """)
        self.event_label.setText(self.tr("Waiting..."))

    def get_sampling_rate(self, sampling_rate):
        self.sampling_rate = sampling_rate

    def _start_graphic(self, sampling_rate):
        self.sampling_rate = sampling_rate
        self.exg_channels = self.protocol['channels'].values()
        self.exg_names = self.protocol['channels'].keys()
        self.window_size = 4
        self.num_points = sampling_rate * self.window_size
        self.buffers = {ch: np.zeros(self.num_points) for ch in self.exg_channels}
        self.timestamps = np.linspace(-self.window_size, 0, self.num_points)
        self.last_event = None
        self.last_event_time = 0

        self.plots = []
        self.curvas = []

        self.grafico.clear()
        self.grafico.setBackground('w')

        for i, (ch, name) in enumerate(zip(self.exg_channels, self.exg_names)):
            plot = self.grafico.addPlot(row=i, col=0)
            plot.showAxis('left', False)
            plot.setLabel('left', name)
            if i == 0:
                plot.setTitle(self.tr("Real Time Data"))
            curva = plot.plot(pen=pg.mkPen(color='b', width=1.5))
            self.plots.append(plot)
            self.curvas.append(curva)

        self.grafico_inicializado = True

    def _plot_sample(self, linha):
        try:
            dados = linha[1:-1]
            evento = linha[-1] 

            self.timestamps += 1 / self.sampling_rate

            for i, ch in enumerate(self.exg_channels):
                valor = float(dados[i])
                self.buffers[ch] = np.roll(self.buffers[ch], -1)
                self.buffers[ch][-1] = valor
                self.curvas[i].setData(x=self.timestamps, y=self.buffers[ch])

        except Exception as e:
            print("Erro ao plotar:", e)

    def get_evento_ativo(self, active_event_name, numero_evento_ativo):            
        if active_event_name != self.active_event_name:
            self.numero_evento_ativo = numero_evento_ativo
            self.active_event_name = active_event_name
            self.feedback_controller()

    def feedback_controller(self):
        self.event_label.setText(self.active_event_name)
        cor_dict = {
            -1: ("transparent", "black"),
            0:  ("#95a5a6", "black"),   # cinza claro → texto branco
            11: ("#e74c3c", "white"),   # vermelho → texto branco
            22: ("#2ecc71", "black"),   # verde claro → texto preto
            33: ("#3498db", "white"),   # azul médio → texto branco
            44: ("#9b59b6", "white"),   # roxo → texto branco
            55: ("#f1c40f", "black"),   # amarelo → texto preto
            66: ("#1abc9c", "black"),   # turquesa claro → texto preto
            77: ("#e67e22", "white"),   # laranja → texto branco
            88: ("#34495e", "white"),   # azul escuro → texto branco
            99: ("#d35400", "white"),   # laranja escuro → texto branco
        }
        self.event_label.setStyleSheet(f"""
            background-color: {cor_dict.get(self.numero_evento_ativo)[0]};
            color: {cor_dict.get(self.numero_evento_ativo)[1]};
            font-size: 24px;
            font-weight: bold;
            border: 2px solid {cor_dict.get(self.numero_evento_ativo)[1]};
            border-radius: 10px;
            padding: 20px;
        """)
        if self.audio_feedback:
            threading.Thread(target=beep, args=(440+self.numero_evento_ativo*20, 200), daemon=True).start()

    def _control_audio_feedback(self):
        self.audio_feedback = not self.audio_feedback
        if self.audio_feedback:
            self.btn_audio_feedback.setText(self.tr("Disable audio feedback"))
        else:
            self.btn_audio_feedback.setText(self.tr("Enable audio feedback"))

    def status_controller(self, status, texto):
        if status == 0:
            self.toast = ToastMessage(
                self,
                texto,
                SUCCESS_COLOR)
            self._restore_ui()
        elif status == -1:
            self.toast = ToastMessage(
                self,
                texto,
                ERROR_COLOR)
            self._restore_ui()