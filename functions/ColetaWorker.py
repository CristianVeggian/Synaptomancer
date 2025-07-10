from PyQt6.QtCore import QThread, pyqtSignal
from brainflow.board_shim import BoardShim
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
from time import sleep
import csv
import datetime
import os
import time
import random
import numpy as np

class ColetaWorker(QThread):
    sig_sampling_rate = pyqtSignal(int)
    sig_active_event = pyqtSignal(str, int)
    sig_status = pyqtSignal(int, str)
    sig_sample = pyqtSignal(object)

    def __init__(self, params, board_id, user_data, modo):
        super().__init__()
        self.params = params
        self.board_id = board_id
        self.user_data = user_data
        self.modo = modo
        self._is_running = True

    def run(self):
        try:
            if self.modo == 'visualizar':
                self._acquire_data(save=False, filter=False)
            elif self.modo == 'brutos':
                self._acquire_data(save=True, filter=False)
            elif self.modo ==  'filtrados':
                self._window_size = 4
                self._n_exg_channels = len(BoardShim.get_exg_channels(self.board_id))
                self._exg_channels = BoardShim.get_exg_channels(self.board_id)
                self._sample_buffer = np.empty((self._n_exg_channels, 0))
                self._acquire_data(save=True, filter=True)
            else:
                raise ValueError(f"Modo '{self.modo}' não reconhecido.")
        except Exception as e:
            print(e)
            self.sig_status.emit(-1, str(e))

    def tempo(self, tipo):
        info = self.user_data[f"tempo_{tipo}"]
        return max(0.5, random.gauss(info["mean"], info["std"]))

    def _gera_eventos(self):
        eventos = []
        timestamp_atual = 0.0
        classes_imageticas = [c for c in self.user_data["classes"] if c != "rest"]

        def adicionar_evento(classe, duracao, ciclo):
            nonlocal timestamp_atual
            eventos.append({
                "inicio": round(timestamp_atual, 2),
                "fim": round(timestamp_atual + duracao, 2),
                "classe": classe,
                "ciclo": ciclo
            })
            timestamp_atual += duracao

        adicionar_evento("rest", self.tempo("descanso"), -1)

        for ciclo in range(self.user_data["ciclos"]):
            for classe in classes_imageticas:
                adicionar_evento(classe, self.tempo("imagetica"), ciclo)
                adicionar_evento("rest", self.tempo("descanso"), ciclo)

        adicionar_evento("rest", self.tempo("descanso"), self.user_data["ciclos"])
        return eventos

    def _cria_arquivo_csv(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        nome_arquivo = f"{self.user_data['nome']}_{ts}.csv"
        caminho_arquivo = os.path.join("data", "collected", nome_arquivo)
        nomes_canais = list(self.user_data['canais'].keys())

        with open(caminho_arquivo, "w", newline="") as f:
            csv.writer(f).writerow(['timestamp'] + nomes_canais + ['events'])

        return caminho_arquivo

    def _acquire_data(self, save=False, filter=False):
        self.sig_status.emit(1, "Coleta Iniciada!")
        eventos = self._gera_eventos()
        nomes_canais = list(self.user_data['canais'].keys())
        canais_fisicos = self.user_data['canais'].values()

        caminho_arquivo = self._cria_arquivo_csv() if save else None
        writer = None
        file = None
        if save:
            file = open(caminho_arquivo, "a", newline="")
            writer = csv.writer(file)

        board = BoardShim(self.board_id, self.params)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.sig_sampling_rate.emit(self.sampling_rate)

        board.prepare_session()
        board.start_stream()

        BUFFER_SIZE = int(self.sampling_rate*0.25)
        tempo_inicio = time.time()

        while self._is_running:
            ts = time.time() - tempo_inicio
            if ts >= eventos[-1]["fim"]:
                break

            sleep(BUFFER_SIZE / self.sampling_rate)
            dados = board.get_board_data(BUFFER_SIZE)

            if filter:
                self._num_point = self._window_size * self.sampling_rate
                dados = self._apply_filter(dados)

            for i in range(dados.shape[1]):
                amostra = dados[:, i]
                linha = [ts]

                for nome_canal in nomes_canais:
                    idx_fisico = self.user_data['canais'][nome_canal]
                    linha.append(amostra[idx_fisico])

                evento_ativo = next((ev for ev in eventos if ev["inicio"] <= ts < ev["fim"]), None)

                if evento_ativo:
                    nome_evento = evento_ativo["classe"]
                    codigo_evento = self.user_data["classes"].get(nome_evento, -1)
                    self.sig_active_event.emit(nome_evento, codigo_evento)
                else:
                    codigo_evento = -1
                    self.sig_active_event.emit("none", codigo_evento)

                linha.append(codigo_evento)

                if writer:
                    writer.writerow(linha)

                self.sig_sample.emit(linha)

        board.stop_stream()
        board.release_session()
        if file:
            file.close()

        self.sig_status.emit(0, "Coleta finalizada!")

    def _apply_filter(self, new_data):
        new_data = new_data[self._exg_channels, :]

        data_size = new_data.shape[1]
        self._sample_buffer = np.concatenate((self._sample_buffer, new_data), axis=1)

        if self._sample_buffer.shape[1] > self._num_point:
            excesso = self._sample_buffer.shape[1] - self._num_point
            self._sample_buffer = self._sample_buffer[:, excesso:]

        filtered_buffer = self._sample_buffer.copy()

        for i in range(filtered_buffer.shape[0]):
            DataFilter.detrend(filtered_buffer[i], DetrendOperations.CONSTANT.value)
            DataFilter.perform_bandpass(
                filtered_buffer[i],
                self.sampling_rate,
                8.0, 30.0, 4,
                FilterTypes.BUTTERWORTH_ZERO_PHASE, 0
            )

        return filtered_buffer[:, -data_size:]
