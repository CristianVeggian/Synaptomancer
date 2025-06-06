import os
import json
import pandas as pd
import importlib.util

from os.path import join
from sklearn.pipeline import Pipeline
import mne

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QPushButton, QFileDialog
from interface.components.ToastMessage import ToastMessage


class AbaExecutarPipeline(QWidget):
    def __init__(self):
        super().__init__()

        self.pipeline = None  # Armazena o pipeline scikit-learn
        self.caminho_dados = None # Armazena o path do arquivo de dados

        self.layout_principal = QVBoxLayout(self)

        self.label_pipeline = QLabel("Nenhum arquivo de pipeline selecionado")
        self.botao_buscar_pipeline = QPushButton("Selecionar pipeline")
        self.botao_buscar_pipeline.setStyleSheet("""
            QPushButton {
                padding: 2px 20px;
            }
        """)
        self.botao_buscar_pipeline.clicked.connect(self.buscar_pipeline)

        self.label_dados = QLabel("Nenhum arquivo de dados selecionado")
        self.botao_buscar_dados = QPushButton("Selecionar dados")
        self.botao_buscar_dados.setStyleSheet("""
            QPushButton {
                padding: 2px 20px;
            }
        """)
        self.botao_buscar_dados.clicked.connect(self.buscar_dados)

        self.botao_executar = QPushButton("Executar Pipeline")
        self.botao_executar.setEnabled(False)
        self.botao_executar.clicked.connect(self.executar_pipeline)

        self.formulario = QFormLayout()
        self.formulario.addRow(self.botao_buscar_pipeline, self.label_pipeline)
        self.formulario.addRow(self.botao_buscar_dados, self.label_dados)

        self.layout_principal.addLayout(self.formulario)
        self.layout_principal.addWidget(self.botao_executar)

    def buscar_pipeline(self):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(
            self, "Selecionar pipeline", join("data", "pipelines"), "JSON Files (*.json)")
        if not caminho_arquivo:
            return

        self.label_pipeline.setText(caminho_arquivo.split("/")[-1])

        try:
            with open(caminho_arquivo, 'r') as f:
                dados = json.load(f)

            etapas = []
            for etapa in dados["etapas"]:
                nome_plugin = etapa["plugin"]
                parametros = etapa.get("parametros", {})

                # Corrige nomes de parâmetros inválidos (ex: espaços)
                parametros = {k.replace(" ", "_").replace("º", "o"): v for k, v in parametros.items()}

                # Caminho absoluto para o arquivo method.py do plugin
                caminho = os.path.join("functions", "plugins", nome_plugin, "method.py")

                # Importação dinâmica da classe PluginMethod
                spec = importlib.util.spec_from_file_location("PluginMethod", caminho)
                modulo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modulo)

                classe = getattr(modulo, "PluginMethod")
                instancia = classe(**parametros)

                etapas.append((nome_plugin, instancia))

            self.pipeline = Pipeline(etapas)
            self.botao_executar.setEnabled(True)
            self.label_pipeline.setText(f"{dados['nome']} carregado.")

        except Exception as e:
            self.label_pipeline.setText(f"Erro: {str(e)}")

    def buscar_dados(self):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(
            self, "Selecionar dados (.csv)", join("data", "collected"), "CSV Files (*.csv)")
        if caminho_arquivo:
            self.caminho_dados = caminho_arquivo
            nome_arquivo = os.path.basename(caminho_arquivo)
            self.label_dados.setText(f"{nome_arquivo} selecionado.")

    def carregar_dados_brutos(self, caminho_csv: str, duracao: float):
        """
        Carrega dados de um arquivo CSV e retorna um objeto mne.io.Raw com anotações.

        Parâmetros:
            caminho_csv (str): Caminho para o arquivo .csv
            duracao (float): Duração das anotações

        Retorna:
            mne.io.Raw: Objeto Raw com os dados EEG e anotações
        """
        # Carregar CSV
        df = pd.read_csv(caminho_csv)
        
        # Extrair eventos
        eventos = df[['timestamp', 'events']]
        eventos = eventos.loc[eventos['events'] != 0]

        # Dados do EEG (sem timestamp/events)
        dados_eeg = df.drop(columns=['timestamp', 'events'])
        nomes_canais = dados_eeg.columns.tolist()
        array_dados = dados_eeg.to_numpy()

        # Criar objeto Raw
        info = mne.create_info(ch_names=nomes_canais, sfreq=250, ch_types='eeg')
        raw = mne.io.RawArray(array_dados.T, info)

        # Adicionar anotações
        for tempo, tipo_evento in eventos.values:
            if tipo_evento == 1:
                raw.annotations.append(tempo, duracao, 'movimento')
            else:
                raw.annotations.append(tempo, duracao * 3, 'repouso')

        return raw

    def executar_pipeline(self):
        if not self.pipeline:
            self.label_pipeline.setText("Pipeline não carregado.")
            return

        if not self.caminho_dados:
            self.label_dados.setText("Arquivo de dados não selecionado.")
            return

        try:
            raw = self.carregar_dados_brutos(self.caminho_dados, duracao=5.0)

            # Pré-processamento fixo por enquanto (pode virar parâmetros depois)
            montage = mne.channels.make_standard_montage("standard_1005")
            raw.set_montage(montage)
            raw.filter(8.0, 25.0, method='iir', skip_by_annotation="edge")

            events, _ = mne.events_from_annotations(raw, event_id=dict(rest=0, move=1))
            picks = mne.pick_types(raw.info, meg=False, eeg=True, stim=False, eog=False, exclude="bads")

            tmin, tmax = -1.0, 4.0
            epochs = mne.Epochs(raw, events, dict(rest=0, move=1), tmin=tmin, tmax=tmax,
                            proj=True, picks=picks, baseline=None, preload=True)
            epochs_train = epochs.copy().crop(tmin=1.0, tmax=2.0)
            labels = epochs.events[:, -1]

            X = epochs_train.get_data()
            y = labels

            self.pipeline.fit(X, y)

            ToastMessage(self, "Pipeline executado com sucesso.")

        except Exception as e:
            ToastMessage(self, f"Erro ao executar: {str(e)}", color="#ff0f0f")