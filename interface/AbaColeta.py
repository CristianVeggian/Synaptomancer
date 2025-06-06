from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QLabel
from interface.AbaColetarDados import AbaColetarDados
from interface.AbaPerfilColeta import AbaPerfilColeta

class AbaColeta(QWidget):
    def __init__(self):
        super().__init__()

        layout_principal = QVBoxLayout()

        # Criar o widget de abas
        self.abas = QTabWidget()

        # Criar abas individuais
        self.aba1 = AbaColetarDados()
        self.aba2 = AbaPerfilColeta()

        # Adiciona as abas ao widget
        self.abas.addTab(self.aba1, "Coletar dados")
        self.abas.addTab(self.aba2, "Criar perfil")

        # Adiciona o QTabWidget ao layout principal
        layout_principal.addWidget(self.abas)
        self.setLayout(layout_principal)