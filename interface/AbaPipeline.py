from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from interface.AbaExecutarPipeline import AbaExecutarPipeline
from interface.AbaCriarPipeline import AbaCriarPipeline

class AbaPipeline(QWidget):
    def __init__(self):
        super().__init__()

        layout_principal = QVBoxLayout()

        # Criar o widget de abas
        self.abas = QTabWidget()

        # Criar abas individuais
        self.aba1 = AbaExecutarPipeline()
        self.aba2 = AbaCriarPipeline()

        # Adiciona as abas ao widget
        self.abas.addTab(self.aba1, "Executar Pipeline")
        self.abas.addTab(self.aba2, "Criar Pipeline")

        # Adiciona o QTabWidget ao layout principal
        layout_principal.addWidget(self.abas)
        self.setLayout(layout_principal)