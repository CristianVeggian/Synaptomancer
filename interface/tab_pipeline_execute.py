from PyQt6.QtWidgets import QVBoxLayout, QFormLayout, QLabel, QPushButton, QFileDialog
from interface.translatable_widget import TranslatableWidget
from interface.components.toast_message import ToastMessage

from functions.run_pipeline import RunPipeline
from functions.utils.paths import PIPELINES_DIR, ACQUISITIONS_DIR
from functions.utils.color import SUCCESS_COLOR, ERROR_COLOR

import os


class TabPipelineExecute(TranslatableWidget):
    def __init__(self):
        super().__init__()
        self.data_path = None
        self.pipeline_path = None

        self.main_layout = QVBoxLayout(self)

        self.label_pipeline = QLabel(self.tr("No pipeline selected"))
        self.label_data = QLabel(self.tr("No data selected"))

        self.btn_pipeline = QPushButton(self.tr("Select pipeline"))
        self.btn_data = QPushButton(self.tr("Select data file"))
        self.btn_execute = QPushButton(self.tr("Execute"))
        self._update_execute_state()

        self.btn_pipeline.clicked.connect(self._search_pipeline)
        self.btn_data.clicked.connect(self._search_data)
        self.btn_execute.clicked.connect(self._execute_pipeline)

        form = QFormLayout()
        form.addRow(self.btn_pipeline, self.label_pipeline)
        form.addRow(self.btn_data, self.label_data)

        self.main_layout.addLayout(form)
        self.main_layout.addWidget(self.btn_execute)

    def _search_pipeline(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select pipeline file"),
            PIPELINES_DIR,
            self.tr("JSON files (*.json)"),
        )

        if not path:
            return

        self.pipeline_path = path
        self.label_pipeline.setText(os.path.basename(path))
        self._update_execute_state()

    def _search_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select data file"),
            ACQUISITIONS_DIR,
            self.tr("CSV files (*.csv)"),
        )

        if not path:
            return

        self.data_path = path
        self.label_data.setText(os.path.basename(path))
        self._update_execute_state()

    def _execute_pipeline(self):
        executor = RunPipeline()
        if not executor.load_pipeline(self.pipeline_path):
            ToastMessage(self, self.tr("Failed to load pipeline"), ERROR_COLOR)
            return

        results = executor.execute(self.data_path)

        if "accuracy" in results:
            acc = results["accuracy"] * 100
            ToastMessage(self, self.tr("Accuracy: {0:.1f}%").format(acc), SUCCESS_COLOR)
        else:
            ToastMessage(
                self, self.tr("Error: {0}").format(results["error"]), ERROR_COLOR
            )

    def _update_execute_state(self):
        self.btn_execute.setEnabled(
            self.pipeline_path is not None and self.data_path is not None
        )
