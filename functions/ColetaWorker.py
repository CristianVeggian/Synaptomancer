from PyQt6.QtCore import QThread, pyqtSignal
from brainflow.board_shim import BoardShim
from time import sleep
import csv, datetime, os, time, random

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
        # 3. Ler os dados [OK]
        # 4. Salvar em um arquivo [OK]
        # 5. Enviar pro gráfico [OK]

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
            BUFFER_SIZE = 10
            sampling_rate = BoardShim.get_sampling_rate(self.board_id)
            
            # Gerar timestamps de eventos:
            # Cria uma fila com os timestamps de quando os eventos vão mudar
            # Analisa no código quando mudar e gerencia a lógica

            eventos = self._gera_eventos()

            with open(self.arquivo_path, "a", newline="") as f:
                writer = csv.writer(f)
                ti = time.time()

                while self._is_running:
                    if time.time() - ti >= eventos[-1]["fim"]:  # para no fim do último evento
                        break

                    sleep(1 / sampling_rate)
                    dados = board.get_board_data(BUFFER_SIZE)

                    for i in range(dados.shape[1]):
                        ts = time.time() - ti
                        amostra = dados[:, i]
                        linha = [ts]

                        for nome_canal in self.canais_nomes:
                            idx_fisico = self.user_data['canais'][nome_canal]
                            linha.append(amostra[idx_fisico])

                        # 🔍 Determinar qual evento está ativo no timestamp atual
                        evento_ativo = next(
                            (ev for ev in eventos if ev["inicio"] <= ts < ev["fim"]),
                            None
                        )
                        if evento_ativo:
                            codigo_evento = self.user_data["classes"][evento_ativo["classe"]]
                        else:
                            codigo_evento = -1  # fora de qualquer evento

                        linha.append(codigo_evento)
                        writer.writerow(linha)

                        self.nova_amostra.emit(amostra)
            
            board.stop_stream()
            print(board.get_board_data_count())
            board.release_session()
            self.coleta_finalizada.emit()

        except Exception as e:
            self.erro.emit(str(e))

    def tempo(self, tipo):
        info = self.user_data[f"tempo_{tipo}"]
        return max(0.5, random.gauss(info["mean"], info["std"]))

    def _gera_eventos(self):

        eventos = []
        timestamp_atual = 0.0
        classes_imageticas = [c for c in self.user_data["classes"] if c != "rest"]

        # REST inicial
        duracao = self.tempo("descanso")
        eventos.append({
            "inicio": round(timestamp_atual, 2),
            "fim": round(timestamp_atual + duracao, 2),
            "classe": "rest",
            "ciclo": -1
        })
        timestamp_atual += duracao

        # Ciclos com imagéticas + rests intermediários
        for ciclo in range(self.user_data["ciclos"]):
            for classe in classes_imageticas:
                # Imagética
                duracao = self.tempo("imagetica")
                eventos.append({
                    "inicio": round(timestamp_atual, 2),
                    "fim": round(timestamp_atual + duracao, 2),
                    "classe": classe,
                    "ciclo": ciclo
                })
                timestamp_atual += duracao

                # REST após imagética
                duracao = self.tempo("descanso")
                eventos.append({
                    "inicio": round(timestamp_atual, 2),
                    "fim": round(timestamp_atual + duracao, 2),
                    "classe": "rest",
                    "ciclo": ciclo
                })
                timestamp_atual += duracao

        # REST final
        duracao = self.tempo("descanso")
        eventos.append({
            "inicio": round(timestamp_atual, 2),
            "fim": round(timestamp_atual + duracao, 2),
            "classe": "rest",
            "ciclo": self.user_data["ciclos"]
        })

        return eventos
