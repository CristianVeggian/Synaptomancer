import json
from os.path import join
from serial.tools.list_ports import comports
from interface.components.ToastMessage import ToastMessage
from functions.ColetaWorker import ColetaWorker
from brainflow import BrainFlowInputParams
from brainflow.board_shim import BoardIds

from functions.utils.boardconfig import board_details

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
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
        self.input_port = QLineEdit()
        self.label_timeout = QLabel("Timeout:")
        self.field_timeout = QDoubleSpinBox()

        self.combo_serial.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.field_mac.setPlaceholderText("xx:xx:xx:xx:xx:xx")
        self.input_port.setPlaceholderText("Escolha uma porta livre...")
        self.input_port.setText("6987")
        self.field_ip.setPlaceholderText("xxx.xxx.xxx.xxx")
        self.field_timeout.setValue(15)

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
        self.campos_dinamicos_layout.addRow(self.label_port, self.input_port)
        self.campos_dinamicos_layout.addRow(self.label_mac, self.field_mac)
        self.campos_dinamicos_layout.addRow(self.label_timeout, self.field_timeout)

        # Botão de coleta
        main_layout.addWidget(self.botao_iniciar_coleta)
        main_layout.addStretch(1)

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
        self.input_port.hide()
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
            self.input_port.show()

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
        placa_selecionada_nome = self.combo_placas.currentText()
        caminho_perfil = self.perfil_lineEdit.text()
        params = BrainFlowInputParams()

        if self.connection_types[placa_selecionada_nome].get('serial', False):
            porta = self.combo_serial.currentText()
            if not porta or porta == "Nenhuma porta":
                self.toast = ToastMessage(self, "Selecione uma porta serial.", "#cc0000")
                return
            params.serial_port = porta

        if self.connection_types[placa_selecionada_nome].get('mac', False):
            mac = self.field_mac.text().strip()
            if not mac:
                self.toast = ToastMessage(self, "Informe o endereço MAC.", "#cc0000")
                return
            params.mac_address = mac

        if self.connection_types[placa_selecionada_nome].get('ip_address', False):
            ip = self.field_ip.text().strip()
            if not ip:
                self.toast = ToastMessage(self, "Informe o endereço IP.", "#cc0000")
                return
            params.ip_address = ip

        if self.connection_types[placa_selecionada_nome].get('port', False):
            params.ip_port = int(self.input_port.text())

        if self.connection_types[placa_selecionada_nome].get('timeout', False):
            params.timeout = self.field_timeout.value()

        if not caminho_perfil:
            self.toast = ToastMessage(self, "Selecione um arquivo de perfil.", "#cc0000")
            return

        try:
            board_id = BoardIds[placa_selecionada_nome].value
        except KeyError:
            self.toast = ToastMessage(self, f"Nome de placa inválido: {placa_selecionada_nome}", "#cc0000")
            return

        try:
            with open(caminho_perfil, 'r') as f:
                user_data = json.load(f)
        except Exception as e:
            self.toast = ToastMessage(self, f"Erro ao carregar perfil: {str(e)}", "#cc0000")
            return

        self.toast = ToastMessage(self, f"Iniciando coleta com placa {placa_selecionada_nome}", "#0077cc")

        if hasattr(self, 'worker') and self.worker.isRunning():
            self.toast = ToastMessage(self, "Coleta já está em andamento.", "#cc0000")
            return

        self.botao_iniciar_coleta.setEnabled(False)
        self.combo_serial.setEnabled(False)
        self.combo_placas.setEnabled(False)
        self.perfil_lineEdit.setEnabled(False)
        self.perfil_botao_buscar.setEnabled(False)

        self.worker = ColetaWorker(params=params, placa_id=board_id, user_data=user_data)
        self.worker.atualiza_status.connect(lambda texto: ToastMessage(self, texto, "#0077cc"))
        self.worker.coleta_finalizada.connect(self.coleta_finalizada)
        self.worker.erro.connect(self.coleta_erro)
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
