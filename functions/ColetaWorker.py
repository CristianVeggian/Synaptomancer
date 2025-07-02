from PyQt6.QtCore import QThread, pyqtSignal
from brainflow.board_shim import BoardShim
from time import sleep
import csv
import datetime
import os
import time
import random


class ColetaWorker(QThread):
    sampling_rate = pyqtSignal(int)
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
                self._visualizar(salvar=False)
            elif self.modo in ['brutos', 'filtrados']:
                self._visualizar(salvar=True)
            else:
                raise ValueError(f"Modo '{self.modo}' não reconhecido.")
        except Exception as e:
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

    def _visualizar(self, salvar=False):
        eventos = self._gera_eventos()
        nomes_canais = list(self.user_data['canais'].keys())
        canais_fisicos = self.user_data['canais'].values()

        caminho_arquivo = self._cria_arquivo_csv() if salvar else None
        writer = None
        file = None
        if salvar:
            file = open(caminho_arquivo, "a", newline="")
            writer = csv.writer(file)

        board = BoardShim(self.board_id, self.params)
        taxa_amostragem = BoardShim.get_sampling_rate(self.board_id)
        self.sampling_rate.emit(taxa_amostragem)

        board.prepare_session()
        board.start_stream()

        BUFFER_SIZE = 10
        tempo_inicio = time.time()

        while self._is_running:
            ts = time.time() - tempo_inicio
            if ts >= eventos[-1]["fim"]:
                break

            sleep(1 / taxa_amostragem)
            dados = board.get_board_data(BUFFER_SIZE)

            for i in range(dados.shape[1]):
                amostra = dados[:, i]
                linha = [ts]

                for nome_canal in nomes_canais:
                    idx_fisico = self.user_data['canais'][nome_canal]
                    linha.append(amostra[idx_fisico])

                evento_ativo = next(
                    (ev for ev in eventos if ev["inicio"] <= ts < ev["fim"]),
                    None
                )

                if evento_ativo:
                    nome_evento = evento_ativo["classe"]
                    codigo_evento = self.user_data["classes"].get(nome_evento, -1)
                    self.sig_active_event.emit(nome_evento, codigo_evento)  # 🚀 Aqui você emite o nome do evento
                else:
                    codigo_evento = -1
                    self.sig_active_event.emit("none", codigo_evento)

                linha.append(codigo_evento)

                if writer:
                    writer.writerow(linha)

                self.sig_sample.emit(amostra)

        board.stop_stream()
        board.release_session()
        if file:
            file.close()

        self.sig_status.emit(0, "Coleta finalizada!")
