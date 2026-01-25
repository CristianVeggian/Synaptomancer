# interface/AbaExecutarPipeline.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QPushButton, QFileDialog
from interface.components.ToastMessage import ToastMessage
from functions.RunPipeline import RunPipeline
import os

class AbaExecutarPipeline(QWidget):
    def __init__(self):
        super().__init__()
        self.executor = RunPipeline()  # ← Injeta!
        
        self.setup_ui()
    
    def setup_ui(self):
        self.layout_principal = QVBoxLayout(self)
        self.label_pipeline = QLabel("Nenhum pipeline")
        self.label_dados = QLabel("Nenhum dado")
        
        self.btn_pipeline = QPushButton("Selecionar Pipeline")
        self.btn_dados = QPushButton("Selecionar Dados")
        self.btn_executar = QPushButton("▶️ Executar")
        self.btn_executar.setEnabled(False)
        
        self.btn_pipeline.clicked.connect(self.buscar_pipeline)
        self.btn_dados.clicked.connect(self.buscar_dados)
        self.btn_executar.clicked.connect(self.executar)
        
        form = QFormLayout()
        form.addRow(self.btn_pipeline, self.label_pipeline)
        form.addRow(self.btn_dados, self.label_dados)
        
        self.layout_principal.addLayout(form)
        self.layout_principal.addWidget(self.btn_executar)
    
    def buscar_pipeline(self):
        path, _ = QFileDialog.getOpenFileName(self, "", "data/pipelines", "JSON (*.json)")
        if path and self.executor.load_pipeline(path):
            self.label_pipeline.setText(f"✅ {os.path.basename(path)}")
            self.btn_executar.setEnabled(True)
        else:
            self.label_pipeline.setText("❌ Erro carregamento")
    
    def buscar_dados(self):
        path, _ = QFileDialog.getOpenFileName(self, "", "data/collected", "CSV (*.csv)")
        if path:
            self.dados_path = path
            self.label_dados.setText(f"✅ {os.path.basename(path)}")
    
    def executar(self):
        if not self.dados_path:
            ToastMessage(self, "❌ Selecione dados!", "#ff6b6b")
            return
        
        resultado = self.executor.execute(self.dados_path)
        if "accuracy" in resultado:
            acc = resultado["accuracy"] * 100
            ToastMessage(self, f"✅ Accuracy: {acc:.1f}%", "#28a745")
        else:
            ToastMessage(self, f"❌ {resultado['error']}", "#ff6b6b")
