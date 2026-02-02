from PyQt6.QtCore import QThread, pyqtSignal
from scipy.signal import butter, iirnotch, filtfilt, lfilter

from functions.utils.paths import ACQUISITIONS_DIR

import csv
import datetime
import os
import time
import serial
import json
import numpy as np

class AcquisitionWorkerECG(QThread):
    sig_sampling_rate = pyqtSignal(int)
    sig_status = pyqtSignal(int, str)
    sig_sample = pyqtSignal(object)

    def __init__(self, params, protocol_path, profile_path, mode=1):
        super().__init__()
        self.mode = mode
        self.params = params
        try:
            with open(protocol_path, "r", encoding="utf-8") as f:
                self.protocol = json.load(f)
            with open(profile_path, "r", encoding="utf-8") as f:
                self.profile = json.load(f)
        except Exception as e:
            self.sig_status.emit(-1, str(e))
        self._is_running = True

    def run(self):
        self.fs = int(self.protocol["sampling_rate_hz"])
        self.filter_cfg = self.protocol.get("filter", {"enabled": False})

        self.window_size_sec = 4
        self.window_samples = int(self.window_size_sec * self.fs)

        self.signal_buffer = np.zeros(self.window_samples)
        try:
            if self.mode == 0:
                self._acquire_data(save=False)
            elif self.mode == 1:
                self._acquire_data(save=True)
        except Exception as e:
            self.sig_status.emit(-1, str(e))

    def _create_csv_file(self):
        ts = datetime.datetime.now().strftime("%d%m%y%H%M%S")

        file_name = f"{self.profile['participant_id']}_{self.protocol['name']}_{ts}.csv"
        file_path = os.path.join(ACQUISITIONS_DIR, file_name)

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["timestamp","signal"]
            writer.writerow(header)

        return file_path

    def _acquire_data(self, save=False):
        self.sig_status.emit(1, "ACQUISITION_STARTED")
        self.sig_sampling_rate.emit(int(self.protocol["sampling_rate_hz"]))

        duration = float(self.protocol["duration_sec"])
        fs = int(self.protocol["sampling_rate_hz"])

        with serial.Serial(self.params["serial_port"],
                        self.params["baud_rate"],
                        timeout=1) as ser:

            ser.write(f"FS:{fs}\n".encode())
            ser.write(f"DUR:{int(duration)}\n".encode())
            time.sleep(0.1)
            ser.write(b"START\n")

            start_time = time.time()

            if save:
                file_path = self._create_csv_file()
                f = open(file_path, "a", newline="")
                writer = csv.writer(f)

            while self._is_running:
                line = ser.readline().decode().strip()

                if line == "END":
                    break

                if line.startswith("DATA;"):
                    try:
                        value = float(line.split(";")[1])
                    except ValueError:
                        continue

                    elapsed = time.time() - start_time

                    self.signal_buffer = np.roll(self.signal_buffer, -1)
                    self.signal_buffer[-1] = value

                    filtered_buffer = self._apply_filter(self.signal_buffer)

                    filtered_value = filtered_buffer[-1]

                    self.sig_sample.emit((elapsed, filtered_value))

                    if save:
                        writer.writerow([elapsed, filtered_value])

            if save:
                f.close()

        self.sig_status.emit(2, "ACQUISITION_COMPLETED")

    def _apply_filter(self, signal):
        cfg = self.filter_cfg

        if not cfg.get("enabled", False):
            return signal

        fs = self.fs
        order = cfg.get("order", 4)
        zero_phase = cfg.get("zero_phase", True)
        ftype = cfg["type"]

        if ftype == "bandpass":
            b, a = butter(
                order,
                [cfg["lowcut"], cfg["highcut"]],
                btype="bandpass",
                fs=fs
            )

        elif ftype == "highpass":
            b, a = butter(
                order,
                cfg["cutoff"],
                btype="highpass",
                fs=fs
            )

        elif ftype == "lowpass":
            b, a = butter(
                order,
                cfg["cutoff"],
                btype="lowpass",
                fs=fs
            )

        elif ftype == "notch":
            Q = cfg["center_freq"] / cfg["bandwidth"]
            b, a = iirnotch(cfg["center_freq"], Q, fs)

        else:
            raise ValueError(f"Unsupported filter type: {ftype}")

        try:
            if zero_phase:
                return filtfilt(b, a, signal)
            else:
                return lfilter(b, a, signal)
        except Exception:
            return signal
