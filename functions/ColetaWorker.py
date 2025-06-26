from PyQt6.QtCore import QThread, pyqtSignal
from brainflow.board_shim import BoardShim
from time import sleep
import numpy as np
import csv, os, datetime

class ColetaWorker(QThread):
    atualiza_status = pyqtSignal(str)
    coleta_finalizada = pyqtSignal()
    erro = pyqtSignal(str)

    def __init__(self, params, placa_id, user_data):
        super().__init__()
        self.params = params
        self.placa_id = placa_id
        self.user_data = user_data

    def run(self):
        try:

            # Instanciar a placa primeiro
            board = BoardShim(self.placa_id, self.params)

            # Pegar os parâmetros da placa
            taxa = BoardShim.get_sampling_rate(self.placa_id)

            #eeg_indices = BoardShim.get_eeg_channels(self.placa_id)
            #eeg_nomes = BoardShim.get_eeg_names(self.placa_id)

            #mapa_nome_para_indice = dict(zip(eeg_nomes, eeg_indices))
            #indices_desejados = #[mapa_nome_para_indice[nome] for nome in self.user_data['canais']]

            descanso = self.user_data['tempo_descanso']
            imagetica = self.user_data['tempo_imagetica']
            execucoes = self.user_data['execucoes']

            eventos = self.criar_eventos(taxa, execucoes, descanso, imagetica)

            # E.g. Uma coleta de 3 execuções, com 4 seg de descanso e 2 de imagética, na cyton tem:

            # Canal de tempo e eventos
            timestamp_idx = BoardShim.get_timestamp_channel(self.placa_id)
            event_idx = BoardShim.get_marker_channel(self.placa_id)

            # Criação do CSV
            nome_arquivo = f"{self.user_data['nome']}-{datetime.datetime.now().strftime('%y-%m-%d-%H-%M-%S')}.csv"
            caminho = os.path.join('data', 'collected', nome_arquivo)
            os.makedirs(os.path.dirname(caminho), exist_ok=True)

            with open(caminho, 'w', newline='') as f_csv:
                fieldnames = ['timestamp'] + self.user_data['canais'] + ['events']
                writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
                writer.writeheader()
            
            # Coleta e já salva os dados

            board.prepare_session()
            board.start_stream()

            with open(caminho, mode='a', newline='') as arquivo_csv:
                writer = csv.writer(arquivo_csv)
                for evento in eventos:
                    if evento != 0.0:
                        board.insert_marker(evento)
                    
                    sleep(1)  # espera 1 amostra

                    amostra = board.get_board_data(1)
                    print(amostra)
                    linha = [amostra[timestamp_idx][0]] + [amostra[idx][0] for idx in self.user_data['canais']] + [amostra[event_idx][0]]
                    writer.writerow(linha)

        except Exception as e:
            print(str(e))
            self.erro.emit(str(e))

    def criar_eventos(self, taxa, execucoes, descanso, imagetica):
        eventos = []
        for _ in range(execucoes):
            for _ in range(round(taxa * descanso)):
                eventos.append(0.0)
            for _ in range(round(taxa * imagetica)):
                eventos.append(11.0)
            for _ in range(round(taxa * descanso)):
                eventos.append(0.0)
            for _ in range(round(taxa * imagetica)):
                eventos.append(22.2)
            for _ in range(round(taxa * descanso)):
                eventos.append(0.0)

        return eventos
            