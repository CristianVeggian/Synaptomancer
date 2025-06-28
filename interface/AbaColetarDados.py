import json
from os.path import join
from serial.tools.list_ports import comports
from interface.components.ToastMessage import ToastMessage
from functions.ColetaWorker import ColetaWorker
from brainflow import BrainFlowInputParams
from brainflow.board_shim import BoardIds

import numpy as np

from functions.utils.boardconfig import board_details

import pyqtgraph as pg
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QIntValidator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFileDialog, QSizePolicy, QDoubleSpinBox,
    QFormLayout, QHBoxLayout
)

class AbaColetarDados(QWidget):
    def __init__(self):
        super().__init__()

        # Botão atualizar portas
        self.button_serial = QPushButton()
        try:
            icon_path = join('interface', 'assets', 'refresh.png')
            if not QIcon(icon_path).isNull():
                self.button_serial.setIcon(QIcon(icon_path))
            else:
                self.button_serial.setText("↻")
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}. Usando texto.")
            self.button_serial.setText("↻")

        self.button_serial.setIconSize(QSize(20, 20))
        self.button_serial.setToolTip("Atualizar portas")
        self.button_serial.setFixedSize(28, 28)
        self.button_serial.clicked.connect(self.atualizar_ports)

        # Placa
        self.label_placa = QLabel("Placa:")
        self.combo_placas = QComboBox()
        self.combo_placas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        placas = [placa.name for placa in BoardIds if placa not in (BoardIds.STREAMING_BOARD, BoardIds.PLAYBACK_FILE_BOARD)]
        self.combo_placas.addItems(placas)
        self.combo_placas.setCurrentIndex(0)

        # Perfil
        self.label_perfil = QLabel("Perfil:")
        self.perfil_lineEdit = QLineEdit()
        self.perfil_lineEdit.setPlaceholderText("Selecione o arquivo de perfil...")
        self.perfil_lineEdit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.perfil_botao_buscar = QPushButton("Buscar")
        self.perfil_botao_buscar.clicked.connect(self.buscar_perfil)

        # Botão principal
        self.botao_iniciar_coleta = QPushButton("Iniciar Coleta")
        self.botao_iniciar_coleta.clicked.connect(self.iniciar_coleta)

        # Campos de conexão
        self.label_serial = QLabel("Porta:")
        self.combo_serial = QComboBox()
        self.label_mac = QLabel("MAC:")
        self.field_mac = QLineEdit()
        self.label_ip = QLabel("Endereço IP:")
        self.field_ip = QLineEdit()
        self.label_port = QLabel("Porta:")
        self.field_port = QLineEdit()
        self.label_timeout = QLabel("Timeout:")
        self.field_timeout = QDoubleSpinBox()

        self.combo_serial.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.field_mac.setPlaceholderText("xx:xx:xx:xx:xx:xx")
        self.field_port.setValidator(QIntValidator(1, 65535))
        self.field_port.setPlaceholderText("Escolha uma porta WiFi")
        self.field_port.setText("6987")
        self.field_ip.setPlaceholderText("xxx.xxx.xxx.xxx")
        self.field_timeout.setValue(15)

        # Função de gráfico
        self.grafico = pg.GraphicsLayoutWidget()

        # Inicialize estruturas vazias
        self.plots = []
        self.curvas = []
        self.buffers = {}
        self.grafico_inicializado = False

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Layout fixo
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        form_layout.addWidget(self.label_placa, 0, 0, Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.combo_placas, 0, 1)
        form_layout.addWidget(self.label_perfil, 1, 0, Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.perfil_lineEdit, 1, 1)
        form_layout.addWidget(self.perfil_botao_buscar, 1, 2)
        form_layout.setColumnStretch(1, 1)

        main_layout.addLayout(form_layout)

        # Layout dinâmico (campos de conexão)
        self.campos_dinamicos_layout = QFormLayout()
        self.campos_dinamicos_widget = QWidget()
        self.campos_dinamicos_widget.setLayout(self.campos_dinamicos_layout)
        main_layout.addWidget(self.campos_dinamicos_widget)

        # Adiciona os campos (eles serão mostrados/ocultados depois)
        serial_layout = QHBoxLayout()
        serial_layout.addWidget(self.combo_serial)
        serial_layout.addWidget(self.button_serial)
        self.campos_dinamicos_layout.addRow(self.label_serial, serial_layout)

        self.campos_dinamicos_layout.addRow(self.label_ip, self.field_ip)
        self.campos_dinamicos_layout.addRow(self.label_port, self.field_port)
        self.campos_dinamicos_layout.addRow(self.label_mac, self.field_mac)
        self.campos_dinamicos_layout.addRow(self.label_timeout, self.field_timeout)

        # Botão de coleta
        main_layout.addWidget(self.botao_iniciar_coleta)
        main_layout.addStretch(1)

        main_layout.addWidget(self.grafico)

        self.connection_types = board_details

        self.atualizar_ports()
        self.combo_placas.currentTextChanged.connect(self.ajustar_interface_conexao)
        self.ajustar_interface_conexao(self.combo_placas.currentText())

    def ajustar_interface_conexao(self, nome_placa):
        conexao = self.connection_types.get(nome_placa, {})

        # Esconde todos
        self.label_serial.hide()
        self.combo_serial.hide()
        self.button_serial.hide()
        self.label_mac.hide()
        self.field_mac.hide()
        self.label_ip.hide()
        self.field_ip.hide()
        self.label_port.hide()
        self.field_port.hide()
        self.label_timeout.hide()
        self.field_timeout.hide()

        # Exibe conforme necessário
        if 'serial' in conexao:
            self.label_serial.show()
            self.combo_serial.show()
            self.button_serial.show()
            self.atualizar_ports()

        if 'mac' in conexao:
            self.label_mac.show()
            self.field_mac.show()

        if 'ip_address' in conexao:
            self.label_ip.show()
            self.field_ip.show()

        if 'port' in conexao:
            self.label_port.show()
            self.field_port.show()

        if 'timeout' in conexao:
            self.label_timeout.show()
            self.field_timeout.show()

        self.connection = conexao

    def atualizar_ports(self):
        try:
            ports = [port.device for port in comports()]
            self.combo_serial.clear()
            if not ports:
                self.combo_serial.addItem("Nenhuma porta")
                self.combo_serial.setEnabled(False)
            else:
                self.combo_serial.addItems(ports)
                self.combo_serial.setEnabled(True)
        except Exception as e:
            self.toast = ToastMessage(self, f"Erro ao listar portas: {str(e)}", "#ff0f0f")

    def buscar_perfil(self):
        initial_dir = join("data", "profiles")
        fileName, _ = QFileDialog.getOpenFileName(self,
                        "Selecionar Arquivo de Perfil",
                        initial_dir,
                        "JSON Files (*.json);;All Files (*)")
        if fileName:
            self.perfil_lineEdit.setText(fileName)

    def iniciar_coleta(self):
        nome_placa = self.combo_placas.currentText()
        caminho_perfil = self.perfil_lineEdit.text()
        
        if not caminho_perfil:
            self.toast = ToastMessage(self, "Selecione um arquivo de perfil.", "#cc0000")
            return
        
        conexao = self.connection_types.get(nome_placa, {})

        params = BrainFlowInputParams()

        if 'serial' in conexao:
            serial = self.combo_serial.currentText()
            if conexao['serial'] and not serial:
                self.toast = ToastMessage(self, "Selecione uma porta serial.", "#cc0000")
                return
            params.serial_port = serial

        if 'mac' in conexao:
            mac = self.field_mac.text().strip()
            if conexao['mac'] and not mac:
                self.toast = ToastMessage(self, "Informe o endereço MAC.", "#cc0000")
                return
            params.mac_address = mac

        if 'ip_address' in conexao:
            ip = self.field_ip.text().strip()
            if conexao['ip'] and not ip:
                self.toast = ToastMessage(self, "Informe o endereço IP.", "#cc0000")
                return
            params.ip_address = ip

        if 'port' in conexao:
            porta = self.field_port.text()
            if conexao['port'] and not porta:
                self.toast = ToastMessage(self, "Informe uma porta.", "#cc0000")
                return
            params.ip_port = int(porta)

        if 'timeout' in conexao:
            timeout = self.field_timeout.value()
            if conexao['timeout'] and not timeout:
                self.toast = ToastMessage(self, "Informe um timeout.", "#cc0000")
                return
            params.timeout = timeout

        try:
            board_id = BoardIds[nome_placa].value
        except KeyError:
            self.toast = ToastMessage(self, f"Nome de placa inválido: {nome_placa}", "#cc0000")
            return

        try:
            with open(caminho_perfil, 'r') as f:
                self.user_data = json.load(f)
        except Exception as e:
            self.toast = ToastMessage(self, f"Erro ao carregar perfil: {str(e)}", "#cc0000")
            return

        self.toast = ToastMessage(self, f"Iniciando coleta com placa {nome_placa}", "#0077cc")

        if hasattr(self, 'worker') and self.worker.isRunning():
            self.toast = ToastMessage(self, "Coleta já está em andamento.", "#cc0000")
            return

        self.botao_iniciar_coleta.setEnabled(False)
        self.combo_serial.setEnabled(False)
        self.combo_placas.setEnabled(False)
        self.perfil_lineEdit.setEnabled(False)
        self.perfil_botao_buscar.setEnabled(False)

        self.worker = ColetaWorker(params=params, board_id=board_id, user_data=self.user_data)
        self.worker.sampling_rate.connect(self.inicializar_grafico)
        self.worker.atualiza_status.connect(lambda texto: ToastMessage(self, texto, "#0077cc"))
        self.worker.coleta_finalizada.connect(self.coleta_finalizada)
        self.worker.erro.connect(self.coleta_erro)
        self.worker.nova_amostra.connect(self.plotar_amostra)
        self.worker.start()

    def coleta_finalizada(self):
        ToastMessage(self, "Coleta finalizada", "#00cc44")
        self.restaurar_ui()

    def coleta_erro(self, erro_msg):
        ToastMessage(self, f"Erro na coleta: {erro_msg}", "#cc0000")
        self.restaurar_ui()

    def restaurar_ui(self):
        self.botao_iniciar_coleta.setEnabled(True)
        self.combo_serial.setEnabled(True)
        self.combo_placas.setEnabled(True)
        self.perfil_lineEdit.setEnabled(True)
        self.perfil_botao_buscar.setEnabled(True)

    def inicializar_grafico(self, sampling_rate):
        self.exg_channels = self.user_data['canais'].values()
        self.window_size = 4
        self.num_points = sampling_rate * self.window_size
        self.buffers = {ch: np.zeros(self.num_points) for ch in self.exg_channels}

        self.plots = []
        self.curvas = []

        self.grafico.clear()  # Limpa qualquer coisa anterior
        self.grafico.setBackground('w')

        for i, ch in enumerate(self.exg_channels):
            plot = self.grafico.addPlot(row=i, col=0)
            plot.showAxis('left', True)
            plot.showAxis('bottom', True)
            if i == 0:
                plot.setTitle("Sinais em Tempo Real")
            curva = plot.plot(pen=pg.mkPen(color='b', width=1.5))
            self.plots.append(plot)
            self.curvas.append(curva)

        self.grafico_inicializado = True

    def plotar_amostra(self, amostra):
        try:
            for i, ch in enumerate(self.exg_channels):
                valor = float(amostra[ch])
                self.buffers[ch] = np.roll(self.buffers[ch], -1)
                self.buffers[ch][-1] = valor
                self.curvas[i].setData(self.buffers[ch])

        except Exception as e:
            print("Erro ao plotar:", e)