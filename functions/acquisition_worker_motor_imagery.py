from PyQt6.QtCore import QThread, pyqtSignal
from brainflow.board_shim import BoardShim
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
from time import sleep

from functions.utils.paths import ACQUISITIONS_DIR

import csv
import datetime
import os
import time
import random
import json
import numpy as np


class AcquisitionWorkerMotorImagery(QThread):
    sig_sampling_rate = pyqtSignal(int)
    sig_active_event = pyqtSignal(str, int)
    sig_status = pyqtSignal(int, str)
    sig_sample = pyqtSignal(object)

    def __init__(self, params, board_id, protocol_path, profile_path, mode=1):
        super().__init__()
        self.params = params
        self.board_id = board_id
        self.mode = mode
        try:
            with open(protocol_path, "r", encoding="utf-8") as f:
                self.protocol = json.load(f)
            with open(profile_path, "r", encoding="utf-8") as f:
                self.profile = json.load(f)
        except Exception as e:
            self.sig_status.emit(-1, str(e))
        self._is_running = True

    def run(self):
        try:
            if self.mode == 0:
                self._acquire_data(save=False, filter=False)
            elif self.mode == 1:
                self._acquire_data(save=True, filter=False)
            elif self.mode == 2:
                self._window_size = 4
                self._n_exg_channels = len(BoardShim.get_exg_channels(self.board_id))
                self._exg_channels = BoardShim.get_exg_channels(self.board_id)
                self._sample_buffer = np.empty((self._n_exg_channels, 0))
                self._acquire_data(save=True, filter=True)
        except Exception as e:
            self.sig_status.emit(-1, str(e))

    def _time(self, tipo):
        info = self.protocol[f"{tipo}"]
        return max(0.5, random.gauss(info["mean"], info["std"]))

    def _generate_event(self):
        stimuli = []
        actual_timestamp = 0.0
        motor_imagery_events = [c for c in self.protocol["classes"] if c != "rest"]

        def add_event(event, duration, run):
            nonlocal actual_timestamp
            stimuli.append(
                {
                    "start": round(actual_timestamp, 2),
                    "end": round(actual_timestamp + duration, 2),
                    "class": event,
                    "run": run,
                }
            )
            actual_timestamp += duration

        add_event("rest", self._time("rest_time"), -1)

        for run in range(self.protocol["runs"]):
            for event in motor_imagery_events:
                add_event(event, self._time("motor_imagery_time"), run)
                add_event("rest", self._time("rest_time"), run)

        add_event("rest", self._time("rest_time"), self.protocol["runs"])
        return stimuli

    def _create_csv_file(self):
        ts = datetime.datetime.now().strftime("%d%m%y%H%M%S")

        file_name = f"{self.profile['participant_id']}_{self.protocol['name']}_{ts}.csv"
        file_path = os.path.join(ACQUISITIONS_DIR, file_name)
        channel_names = list(self.protocol["channels"].keys())

        with open(file_path, "w", newline="") as f:
            csv.writer(f).writerow(["timestamp"] + channel_names + ["events"])

        return file_path

    def _acquire_data(self, save=False, filter=False):
        self.sig_status.emit(1, "Coleta Iniciada!")
        events = self._generate_event()
        physical_channels = self.protocol["channels"].values()

        file_path = self._create_csv_file() if save else None
        if save:
            writer = None
            file = None
            file = open(file_path, "a", newline="")
            writer = csv.writer(file)

        board = BoardShim(self.board_id, self.params)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.sig_sampling_rate.emit(self.sampling_rate)

        board.prepare_session()
        board.start_stream()

        BUFFER_SIZE = int(self.sampling_rate * 0.25)
        start_time = time.time()

        while self._is_running:
            ts = time.time() - start_time
            if ts >= events[-1]["end"]:
                break

            sleep(BUFFER_SIZE / self.sampling_rate)
            data = board.get_board_data(BUFFER_SIZE)

            if filter:
                self._num_point = self._window_size * self.sampling_rate
                data = self._apply_filter(data)

            for i in range(data.shape[1]):
                sample = data[:, i]
                linha = [ts]

                for channel in physical_channels:
                    linha.append(sample[channel])

                evento_ativo = next(
                    (ev for ev in events if ev["start"] <= ts < ev["end"]), None
                )

                if evento_ativo:
                    nome_evento = evento_ativo["class"]
                    codigo_evento = self.protocol["classes"].get(nome_evento, -1)
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

        self.sig_status.emit(0, self.tr("Coleta finalizada!"))

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
                8.0,
                30.0,
                4,
                FilterTypes.BUTTERWORTH_ZERO_PHASE,
                0,
            )

        return filtered_buffer[:, -data_size:]
