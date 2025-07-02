import json
import os
import mne
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QScrollArea, QGridLayout,
    QSpinBox, QDoubleSpinBox, QHBoxLayout, QFrame
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
        self.input_descricao.setFixedHeight(self.input_descricao.fontMetrics().height() * 3)

        self.combo_montagem = QComboBox()
        self.combo_montagem.addItems(get_builtin_montages())
        self.combo_montagem.currentTextChanged.connect(self.atualizar_canais)

        self.canais_widget = QWidget()
        self.canais_layout = QGridLayout(self.canais_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.canais_widget)

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
        form_layout.addRow("Canais:", scroll_area)
        form_layout.addRow("Nº de ciclos:", self.input_runs)

        # Classes

        # Botão "+"
        self.btn_add_class = QPushButton("+")
        self.btn_add_class.setToolTip("Adicionar nova etapa ao pipeline")
        self.btn_add_class.setFixedSize(20, 20)
        self.btn_add_class.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #28a745;
                border: none;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.btn_add_class.clicked.connect(self.add_class)

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

                # Área de classes
        self.scroll_layout = QVBoxLayout()
        self.class_widgets = []  # (QLineEdit, QSpinBox)

        classes_container = QWidget()
        classes_container.setLayout(self.scroll_layout)
        classes_scroll = QScrollArea()
        classes_scroll.setWidgetResizable(True)
        classes_scroll.setWidget(classes_container)

        # Linha "Classes:" com botão +
        classes_row = QHBoxLayout()
        classes_row.addWidget(QLabel("Classes:"))
        classes_row.addWidget(self.btn_add_class)
        classes_row.addStretch()

        form_layout.addRow(classes_row)
        form_layout.addRow(classes_scroll)

        # Adiciona uma classe padrão
        self.add_class()

        layout.addLayout(form_layout)

        salvar_btn = QPushButton("Salvar perfil")
        salvar_btn.clicked.connect(self.salvar_perfil)
        layout.addWidget(salvar_btn)

    def atualizar_canais(self, montagem):
        info = mne.create_info(ch_names=[], sfreq=100, ch_types='eeg')
        montage = mne.channels.make_standard_montage(montagem)
        info.set_montage(montage)

        # Limpar canais anteriores
        for i in reversed(range(self.canais_layout.count())):
            widget = self.canais_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.canais_mapeados = {}  # canal lógico → QComboBox

        for i, ch_name in enumerate(montage.ch_names):
            label = QLabel(ch_name)
            combo = QComboBox()
            combo.addItem("Ignorar")  # opcional
            combo.addItems([str(i) for i in range(32)])  # número de canais físicos disponíveis
            self.canais_layout.addWidget(label, i, 0)
            self.canais_layout.addWidget(combo, i, 1)
            self.canais_mapeados[ch_name] = combo

    def salvar_perfil(self):
        nome_perfil = self.input_nome.text().strip()
        if not nome_perfil:
            self.toast = ToastMessage(self, "O nome do perfil não pode estar vazio.")
            return

        canais = {}
        for nome_canal, combo in self.canais_mapeados.items():
            idx = combo.currentIndex()
            if idx > 0:  # Ignorar "Ignorar"
                canais[nome_canal] = int(combo.currentText())

        classes = {}
        for _, nome_input, valor_input in self.class_widgets:
            nome_classe = nome_input.text().strip()
            if nome_classe:
                classes[nome_classe] = valor_input.value()
        if not classes:
            self.toast = ToastMessage(self, "Adicione pelo menos uma classe.")
            return

        perfil = {
            "nome": nome_perfil,
            "descricao": self.input_descricao.toPlainText(),
            "montagem": self.combo_montagem.currentText(),
            "canais": canais,
            "ciclos": self.input_runs.value(),
            "classes": classes,
            "tempo_descanso": {
                "mean": self.input_rest_mean.value(),
                "std": self.input_rest_std.value()
            },
            "tempo_imagetica": {
                "mean": self.input_mi_mean.value(),
                "std": self.input_mi_std.value()
            }
        }

        with open(os.path.join('data','profiles', f"{nome_perfil}.json"), "w", encoding="utf-8") as f:
            json.dump(perfil, f, indent=4)

        self.toast = ToastMessage(self, f"Perfil '{nome_perfil}' salvo com sucesso.")

    def add_class(self):

        # Container do bloco
        container = QFrame()
        layout_class = QHBoxLayout(container)

        # botão de remover
        botao_remover = QPushButton("-")
        botao_remover.setFixedSize(20, 20)
        botao_remover.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #ff0000;
                border: none;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #b30000;
            }
        """)
        botao_remover.clicked.connect(lambda: self.rmv_class(container))

        class_name = QLineEdit("Nome")
        class_value = QSpinBox()
        class_value.setMinimum(0)         # opcional: valor mínimo
        class_value.setMaximum(99)        # define o valor máximo
        class_value.setSingleStep(11)     # incrementa de 11 em 11
        class_value.setValue(0)           # valor inicial
        class_value.valueChanged.connect(self.on_value_changed)

        layout_class.addWidget(class_name)
        layout_class.addWidget(class_value)

        layout_class.addStretch()
        layout_class.addWidget(botao_remover)

        # Adiciona ao layout de scroll
        self.scroll_layout.addWidget(container)
        self.class_widgets.append((container, class_name, class_value))

    def rmv_class(self, container):
        for i, (frame, _, _) in enumerate(self.class_widgets):
            if frame == container:
                self.scroll_layout.removeWidget(frame)
                frame.deleteLater()
                self.class_widgets.pop(i)
                break

    def on_value_changed(self, value):
        spinbox = self.sender()
        if spinbox and value % 11 != 0:
            corrected = round(value / 11) * 11
            spinbox.blockSignals(True)
            spinbox.setValue(corrected)
            spinbox.blockSignals(False)