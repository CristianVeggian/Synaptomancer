import json
from os.path import join
from serial.tools.list_ports import comports
from interface.components.ToastMessage import ToastMessage
from functions.ColetaWorker import ColetaWorker

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFileDialog, QSizePolicy
)
from brainflow.board_shim import BoardIds

class AbaColetarDados(QWidget):
    def __init__(self):
        super().__init__()

        self.label_porta = QLabel("Porta:")
        self.combo_ports = QComboBox()
        self.combo_ports.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.botao_atualizar = QPushButton()
        try:
            icon_path = join('interface', 'assets', 'refresh.png')
            if not QIcon(icon_path).isNull():
                 self.botao_atualizar.setIcon(QIcon(icon_path))
            else:
                print(f"Aviso: Ícone não encontrado em {icon_path}. Usando texto.")
                self.botao_atualizar.setText("↻")
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}. Usando texto.")
            self.botao_atualizar.setText("↻")

        self.botao_atualizar.setIconSize(QSize(20, 20))
        self.botao_atualizar.setToolTip("Atualizar portas")
        self.botao_atualizar.setFixedSize(28, 28)
        self.botao_atualizar.clicked.connect(self.atualizar_ports)

        self.label_placa = QLabel("Placa:")
        self.combo_placas = QComboBox()
        self.combo_placas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        placas = [placa.name for placa in BoardIds if placa not in (BoardIds.STREAMING_BOARD, BoardIds.PLAYBACK_FILE_BOARD)]
        self.combo_placas.addItems(placas)
        no_board_text = "NO_BOARD"
        if no_board_text in placas:
             self.combo_placas.setCurrentText(no_board_text)
        elif placas:
            self.combo_placas.setCurrentIndex(0)

        self.label_perfil = QLabel("Perfil:")
        self.perfil_lineEdit = QLineEdit()
        self.perfil_lineEdit.setPlaceholderText("Selecione o arquivo de perfil...")
        self.perfil_lineEdit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.perfil_botao_buscar = QPushButton("Buscar")
        self.perfil_botao_buscar.clicked.connect(self.buscar_perfil)

        self.botao_iniciar_coleta = QPushButton("Iniciar Coleta")
        self.botao_iniciar_coleta.clicked.connect(self.iniciar_coleta)

        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        form_layout.addWidget(self.label_porta, 0, 0, Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.combo_ports, 0, 1)
        form_layout.addWidget(self.botao_atualizar, 0, 2)


        form_layout.addWidget(self.label_placa, 1, 0, Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.combo_placas, 1, 1)
   
        form_layout.addWidget(self.label_perfil, 2, 0, Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.perfil_lineEdit, 2, 1)
        form_layout.addWidget(self.perfil_botao_buscar, 2, 2)

        form_layout.setColumnStretch(0, 0)
        form_layout.setColumnStretch(1, 1)
        form_layout.setColumnStretch(2, 0)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.botao_iniciar_coleta)
        main_layout.addStretch(1)

        self.atualizar_ports()

    def atualizar_ports(self):
        try:
            ports = [port.device for port in comports()]
            self.combo_ports.clear()
            if not ports:
                self.combo_ports.addItem("Nenhuma porta")
                self.combo_ports.setEnabled(False)
            else:
                self.combo_ports.addItems(ports)
                self.combo_ports.setEnabled(True)
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
            print(f"Arquivo de perfil selecionado: {fileName}")

    def iniciar_coleta(self):
        porta_selecionada = self.combo_ports.currentText()
        placa_selecionada_nome = self.combo_placas.currentText()
        caminho_perfil = self.perfil_lineEdit.text()

        if porta_selecionada == "Nenhuma porta" or not porta_selecionada:
            self.toast = ToastMessage(self, "Selecione uma porta serial.", "#cc0000")
            return

        if not placa_selecionada_nome:
            self.toast = ToastMessage(self, "Selecione uma placa.", "#cc0000")
            return

        if not caminho_perfil:
            self.toast = ToastMessage(self, "Selecione um arquivo de perfil.", "#cc0000")
            return

        user_data = {}
        try:
            with open(caminho_perfil, 'r') as f:
                user_data = json.load(f)
        except FileNotFoundError:
            self.toast = ToastMessage(self, f"Arquivo de perfil não encontrado: {caminho_perfil}", "#cc0000")
            return
        except json.JSONDecodeError:
            self.toast = ToastMessage(self, f"Erro ao decodificar JSON do perfil: {caminho_perfil}", "#cc0000")
            return
        except Exception as e:
            self.toast = ToastMessage(self, f"Erro ao carregar perfil: {str(e)}", "#cc0000")
            return

        try:
            board_id = BoardIds[placa_selecionada_nome].value
        except KeyError:
            self.toast = ToastMessage(self, f"Nome de placa inválido: {placa_selecionada_nome}", "#cc0000")
            return

        self.toast = ToastMessage(self, f"Iniciando coleta: Porta={porta_selecionada}, Placa={placa_selecionada_nome}({board_id})", "#0077cc")

        self.worker = ColetaWorker(porta_serial=porta_selecionada, placa_id=board_id, user_data=user_data)
        self.worker.atualiza_status.connect(lambda texto: ToastMessage(self, texto, "#0077cc"))
        self.worker.coleta_finalizada.connect(lambda: ToastMessage(self, "Coleta finalizada", "#00cc44"))
        self.worker.erro.connect(lambda erro_msg: ToastMessage(self, f"Erro na coleta: {erro_msg}", "#cc0000"))
        self.worker.start()