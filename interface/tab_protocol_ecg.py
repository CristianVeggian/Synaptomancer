from interface.translatable_widget import TranslatableWidget
from interface.components.toast_message import ToastMessage
from interface.components.filter_config_widget import FilterConfigWidget
from functions.utils.color import WARNING_COLOR, SUCCESS_COLOR, ERROR_COLOR
from functions.utils.paths import PROTOCOLS_DIR

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
)

import json
import os


class TabProtocolECG(TranslatableWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout(self)

        self.input_protocol_name = QLineEdit()

        self.input_duration = QDoubleSpinBox()
        self.input_duration.setRange(0, 60)
        self.input_duration.setSuffix(" s")
        self.input_duration.setSingleStep(0.1)

        self.input_sampling_rate = QSpinBox()
        self.input_sampling_rate.setRange(1, 2000)
        self.input_sampling_rate.setSuffix(" Hz")

        form_layout = QFormLayout()
        form_layout.addRow(self.tr("Protocol name"), self.input_protocol_name)
        form_layout.addRow(self.tr("Duration"), self.input_duration)
        form_layout.addRow(self.tr("Sampling Rate"), self.input_sampling_rate)

        filter_layout = QHBoxLayout()

        self.checkbox_apply_filter = QCheckBox()
        self.btn_filter_configs = QPushButton(self.tr("Show Filter Configs"))

        self.btn_filter_configs.setEnabled(False)
        self.btn_filter_configs.clicked.connect(self._toggle_filter_configs)

        filter_layout.addWidget(self.checkbox_apply_filter)
        filter_layout.addWidget(self.btn_filter_configs)

        form_layout.addRow(self.tr("Apply Filter"), filter_layout)
        self.main_layout.addLayout(form_layout)

        self.filter_config_widget = FilterConfigWidget(self)
        self.main_layout.addWidget(self.filter_config_widget)

        self.checkbox_apply_filter.stateChanged.connect(
            self._on_filter_checkbox_changed
        )

        btn_save = QPushButton(self.tr("Save protocol"))
        btn_save.clicked.connect(self._save_protocol)
        self.main_layout.addWidget(btn_save)

    def _toggle_filter_configs(self):
        visible = not self.filter_config_widget.isVisible()
        self.filter_config_widget.setVisible(visible)

        if visible:
            self.btn_filter_configs.setText(self.tr("Hide Filter Configs"))
        else:
            self.btn_filter_configs.setText(self.tr("Filter Configs"))

    def _on_filter_checkbox_changed(self, state):
        enabled = state > 0
        self.btn_filter_configs.setEnabled(enabled)

        if not enabled:
            self.filter_config_widget.setVisible(False)
            self.btn_filter_configs.setText(self.tr("Filter Configs"))

    def _save_protocol(self):
        protocol_name = self.input_protocol_name.text().strip()
        if not protocol_name:
            self.toast = ToastMessage(
                self, self.tr("Protocol name cannot be empty"), WARNING_COLOR
            )
            return

        if self.input_duration.value() <= 0:
            self.toast = ToastMessage(
                self, self.tr("Duration must be greater than zero"), WARNING_COLOR
            )
            return

        protocol = {
            "name": protocol_name,
            "type": "ecg",
            "duration_sec": self.input_duration.value(),
            "sampling_rate_hz": self.input_sampling_rate.value(),
            "filter": self.filter_config_widget.get_filter_config()
            if self.checkbox_apply_filter.isChecked()
            else {"enabled": False},
        }

        try:
            with open(
                os.path.join(PROTOCOLS_DIR, protocol_name + ".json"),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(protocol, f, indent=4)
            self.toast = ToastMessage(
                self,
                self.tr("Protocol '{0}' saved successfully.").format(protocol_name),
                SUCCESS_COLOR,
            )
        except Exception as e:
            self.toast = ToastMessage(
                self,
                self.tr("Failed to save protocol: {0}").format(str(e)),
                ERROR_COLOR,
            )
            return
