from PyQt6.QtCore import QThread, pyqtSignal
from brainflow.board_shim import BoardShim
from time import sleep
import numpy as np
import csv, datetime, os, time

class ColetaWorker(QThread):
    sampling_rate = pyqtSignal(int)
    atualiza_status = pyqtSignal(str)
    nova_amostra = pyqtSignal(object)
    coleta_finalizada = pyqtSignal()
    erro = pyqtSignal(str)

    def __init__(self, params, board_id, user_data):
        super().__init__()
        self.params = params
        self.board_id = board_id
        self.user_data = user_data
        self._is_running = True
        
    def run(self):

        # passo a passo:
        # 1. Criar arquivo para guardar [OK]
        # 2. Instanciar a placa [OK]
        # 3. Ler os dados
        # 4. Salvar em um arquivo
        # 5. Enviar pro gráfico

        try:

            # 1. Criar arquivo para guardar
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.arquivo_nome= f"{self.user_data['nome']}${ts}.csv"
            self.arquivo_path = os.path.join("data","collected",self.arquivo_nome)
            self.canais_nomes = self.user_data['canais'].keys()
            self.canais_fisicos = self.user_data['canais'].values()
            header = ['timestamp'] + list(self.canais_nomes) + ['events']
            with open(self.arquivo_path, "w", newline="") as f:
                csv.writer(f).writerow(header)

            # 2. Instanciar a placa
            board = BoardShim(self.board_id, self.params)
            self.sampling_rate.emit(BoardShim.get_sampling_rate(self.board_id))
            board.prepare_session()

            # 3. Ler os dados
            board.start_stream()
            BUFFER_TAMANHO = 10
            sampling_rate = BoardShim.get_sampling_rate(self.board_id)
            
            with open(self.arquivo_path, "a", newline="") as f:
                writer = csv.writer(f)
                while self._is_running:
                    sleep(BUFFER_TAMANHO / sampling_rate)
                    dados = board.get_board_data(BUFFER_TAMANHO)
                    for i in range(dados.shape[1]):
                        ts = time.time()
                        amostra = dados[:, i]
                        linha = [ts]
                        for nome_canal in self.canais_nomes:
                            idx_fisico = self.user_data['canais'][nome_canal]
                            linha.append(amostra[idx_fisico])
                        linha.append(0)  # eventos placeholder
                        writer.writerow(linha)
                        self.nova_amostra.emit(amostra)

            board.stop_stream()
            board.release_session()
            self.coleta_finalizada.emit()

        except Exception as e:
            self.erro.emit(str(e))

    def stop(self):
        self._is_running = False