from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog, 
                             QListWidget, QProgressBar, QMessageBox, QLabel)
import os, shutil, importlib
from interface.components.ToastMessage import ToastMessage

class AbaGerenciarPlugins(QWidget):
    def __init__(self):
        super().__init__()
        vertical_outter_layout = QVBoxLayout(self)
        horizontal_layout = QHBoxLayout()


        # Lista plugins instalados
        self.lista_plugins = QListWidget()
        vertical_outter_layout.addWidget(QLabel("Plugins Instalados:"))

        vertical_outter_layout.addLayout(horizontal_layout)

        horizontal_layout.addWidget(self.lista_plugins, stretch=3)
        
        # Botões
        btn_instalar = QPushButton("📦 Instalar Novo Plugin")
        btn_atualizar = QPushButton("🔄 Atualizar Lista")
        btn_excluir = QPushButton("🗑️ Remover Plugin")
        
        vertical_inner_layout = QVBoxLayout()

        btn_instalar.clicked.connect(self.instalar_plugin)
        btn_atualizar.clicked.connect(self.atualizar_lista)
        btn_excluir.clicked.connect(self.remover_plugin)

        btn_instalar.setToolTip("Instalar plugin .zip")
        btn_atualizar.setToolTip("Recarregar lista plugins")
        btn_excluir.setToolTip("Remover plugin selecionado")

        vertical_inner_layout.addWidget(btn_instalar)
        vertical_inner_layout.addWidget(btn_atualizar)
        vertical_inner_layout.addWidget(btn_excluir)
        vertical_inner_layout.addStretch()

        horizontal_layout.addLayout(vertical_inner_layout, stretch=1)

        self.atualizar_lista()
    
    def atualizar_lista(self):
        self.lista_plugins.clear()
        plugins_dir = "functions/plugins"
        for plugin in os.listdir(plugins_dir):
            if os.path.isdir(os.path.join(plugins_dir, plugin)):
                self.lista_plugins.addItem(plugin)
    
    def instalar_plugin(self):
        zip_file, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Plugin (.zip)", 
            "", "ZIP (*.zip)"
        )
        if zip_file:
            # Extrair ZIP → functions/plugins/NOME/
            plugin_dir = QFileDialog.getExistingDirectory(
                self, "Pasta destino", "functions/plugins"
            )
            shutil.unpack_archive(zip_file, plugin_dir)
            ToastMessage(self, f"Plugin instalado: {os.path.basename(zip_file)}")
            self.atualizar_lista()
    
    def remover_plugin(self):
        plugin = self.lista_plugins.currentItem()
        if plugin:
            reply = QMessageBox.question(
                self, "Confirmar", f"Remover {plugin.text()}?"
            )
            if reply == QMessageBox.StandardButton.Yes:
                shutil.rmtree(f"functions/plugins/{plugin.text()}")
                ToastMessage(self, "Plugin removido!")
                self.atualizar_lista()
