import json
import os
import mne
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QListWidget,
    QListWidgetItem, QSpinBox
)
from mne.channels import get_builtin_montages
from interface.components.ToastMessage import ToastMessage

class AbaPerfilColeta(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # Campos do perfil
        self.input_nome = QLineEdit()
        self.input_descricao = QTextEdit()

        self.combo_montagem = QComboBox()
        self.combo_montagem.addItems(get_builtin_montages())
        self.combo_montagem.currentTextChanged.connect(self.atualizar_canais)

        self.input_n_canais = QSpinBox()
        self.input_n_canais.setRange(1, 32)

        self.lista_canais = QListWidget()

        self.input_runs = QSpinBox()
        self.input_rest = QSpinBox()
        self.input_mi = QSpinBox()

        # Botão salvar
        self.botao_salvar = QPushButton("Pronto")
        self.botao_salvar.clicked.connect(self.salvar_perfil)

        # Layout visual
        form = QFormLayout()
        form.addRow("Nome", self.input_nome)
        form.addRow("Descrição breve", self.input_descricao)
        form.addRow("Montagem", self.combo_montagem)
        form.addRow("Nº Canais", self.input_n_canais)
        form.addRow("Canais", self.lista_canais)
        form.addRow("Execuções", self.input_runs)
        form.addRow("Tempo de Descanso", self.input_rest)
        form.addRow("Tempo de Imagética", self.input_mi)

        layout.addLayout(form)
        layout.addWidget(self.botao_salvar)

    def atualizar_canais(self):
        nome_montagem = self.combo_montagem.currentText()
        montage = mne.channels.make_standard_montage(nome_montagem)
        canais = montage.ch_names

        self.lista_canais.clear()
        for nome in canais:
            item = QListWidgetItem(nome)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.lista_canais.addItem(item)

    def salvar_perfil(self):
        nome = self.input_nome.text().strip()
        if not nome:
            print("Erro: Nome não pode estar vazio")
            return

        perfil = {
            "nome": nome,
            "descricao": self.input_descricao.toPlainText(),
            "montagem": self.combo_montagem.currentText(),
            "n_canais": self.input_n_canais.value(),
            "canais": [self.lista_canais.item(i).text()
                       for i in range(self.lista_canais.count())
                       if self.lista_canais.item(i).checkState() == Qt.CheckState.Checked],
            "execucoes": self.input_runs.value(),
            "tempo_descanso": self.input_rest.value(),
            "tempo_imagetica": self.input_mi.value()
        }

        # Salvar no diretório de perfis
        os.makedirs(os.path.join("data", "profiles"), exist_ok=True)
        caminho = os.path.join("data", "profiles", f"{nome}.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(perfil, f, indent=4)

        ToastMessage(self, f"Perfil '{nome}' salvo com sucesso.")
