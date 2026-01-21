from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from interface.AbaColeta import AbaColeta
from interface.AbaPipeline import AbaPipeline
from interface.AbaGerenciarPlugins import AbaGerenciarPlugins

class Janela(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synaptomancer")
        self.resize(800, 600)

        layout_principal = QVBoxLayout()

        # Criar o widget de abas
        self.abas = QTabWidget()

        # Criar abas individuais
        self.aba1 = AbaColeta()
        self.aba2 = AbaPipeline()
        self.aba_plugins = AbaGerenciarPlugins()

        # Adiciona as abas ao widget
        self.abas.addTab(self.aba1, "Coletar Dados")
        self.abas.addTab(self.aba2, "Processamento")
        self.abas.addTab(self.aba_plugins, "🔧 Plugins")

        # Adiciona o QTabWidget ao layout principal
        layout_principal.addWidget(self.abas)
        self.setLayout(layout_principal)
        self.showMaximized()