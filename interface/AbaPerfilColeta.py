import json
import os
import mne
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QListWidget,
    QListWidgetItem, QSpinBox, QDoubleSpinBox, QHBoxLayout
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


        self.lista_canais = QListWidget()

        self.input_runs = QSpinBox()
        self.input_runs.setRange(1, 100)

        # Tempo de descanso: média e desvio
        self.input_rest_mean = QDoubleSpinBox()
        self.input_rest_mean.setRange(0, 60)
        self.input_rest_mean.setSuffix(" s")
        self.input_rest_mean.setSingleStep(0.1)

        self.input_rest_std = QDoubleSpinBox()
        self.input_rest_std.setRange(0, 30)
        self.input_rest_std.setSuffix(" s")
        self.input_rest_std.setSingleStep(0.1)

        # Tempo de imagética: média e desvio
        self.input_mi_mean = QDoubleSpinBox()
        self.input_mi_mean.setRange(0, 60)
        self.input_mi_mean.setSuffix(" s")
        self.input_mi_mean.setSingleStep(0.1)

        self.input_mi_std = QDoubleSpinBox()
        self.input_mi_std.setRange(0, 30)
        self.input_mi_std.setSuffix(" s")
        self.input_mi_std.setSingleStep(0.1)

        form_layout = QFormLayout()
        form_layout.addRow("Nome do perfil:", self.input_nome)
        form_layout.addRow("Descrição:", self.input_descricao)
        form_layout.addRow("Montagem:", self.combo_montagem)
        form_layout.addRow("Canais:", self.lista_canais)
        form_layout.addRow("Nº de execuções (runs):", self.input_runs)

        # Campos compostos
        rest_layout = QHBoxLayout()
        rest_layout.addWidget(QLabel("Média:"))
        rest_layout.addWidget(self.input_rest_mean)
        rest_layout.addWidget(QLabel("Desvio:"))
        rest_layout.addWidget(self.input_rest_std)
        form_layout.addRow("Tempo de descanso:", rest_layout)

        mi_layout = QHBoxLayout()
        mi_layout.addWidget(QLabel("Média:"))
        mi_layout.addWidget(self.input_mi_mean)
        mi_layout.addWidget(QLabel("Desvio:"))
        mi_layout.addWidget(self.input_mi_std)
        form_layout.addRow("Tempo de imagética:", mi_layout)

        layout.addLayout(form_layout)

        salvar_btn = QPushButton("Salvar perfil")
        salvar_btn.clicked.connect(self.salvar_perfil)
        layout.addWidget(salvar_btn)

    def atualizar_canais(self, montagem):
        info = mne.create_info(ch_names=[], sfreq=100, ch_types='eeg')
        montage = mne.channels.make_standard_montage(montagem)
        info.set_montage(montage)
        self.lista_canais.clear()
        for ch in montage.ch_names:
            item = QListWidgetItem(ch)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.lista_canais.addItem(item)

    def salvar_perfil(self):
        nome = self.input_nome.text().strip()
        if not nome:
            self.toast = ToastMessage(self, "O nome do perfil não pode estar vazio.")
            return

        canais = []
        for i in range(self.lista_canais.count()):
            item = self.lista_canais.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                canais.append(item.text())

        perfil = {
            "nome": nome,
            "descricao": self.input_descricao.toPlainText(),
            "montagem": self.combo_montagem.currentText(),
            "canais": canais,
            "execucoes": self.input_runs.value(),
            "tempo_descanso": {
                "mean": self.input_rest_mean.value(),
                "std": self.input_rest_std.value()
            },
            "tempo_imagetica": {
                "mean": self.input_mi_mean.value(),
                "std": self.input_mi_std.value()
            }
        }

        with open(os.path.join('data','profiles', f"{nome}.json"), "w", encoding="utf-8") as f:
            json.dump(perfil, f, indent=4)

        self.toast = ToastMessage(self, f"Perfil '{nome}' salvo com sucesso.")