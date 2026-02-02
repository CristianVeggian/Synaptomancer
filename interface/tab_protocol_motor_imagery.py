import json
import os
import mne
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QScrollArea,
    QGridLayout,
    QSpinBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QFrame,
)

from functions.utils.color import WARNING_COLOR, SUCCESS_COLOR, ERROR_COLOR
from functions.utils.paths import PROTOCOLS_DIR

from interface.translatable_widget import TranslatableWidget
from mne.channels import get_builtin_montages
from interface.components.toast_message import ToastMessage


class TabProtocolMotorImagery(TranslatableWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.input_protocol_name = QLineEdit()

        self.combo_montage = QComboBox()
        self.combo_montage.addItems(sorted(get_builtin_montages()))
        self.combo_montage.currentTextChanged.connect(self._refresh_channels)

        self.mapped_channels = {}

        self.widget_channels = QWidget()
        self.layout_channels = QGridLayout(self.widget_channels)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.widget_channels)

        self.input_runs = QSpinBox()
        self.input_runs.setRange(1, 100)

        self.input_rest_mean = QDoubleSpinBox()
        self.input_rest_mean.setRange(0, 60)
        self.input_rest_mean.setSuffix(" s")
        self.input_rest_mean.setSingleStep(0.1)

        self.input_rest_std = QDoubleSpinBox()
        self.input_rest_std.setRange(0, 30)
        self.input_rest_std.setSuffix(" s")
        self.input_rest_std.setSingleStep(0.1)

        self.input_mi_mean = QDoubleSpinBox()
        self.input_mi_mean.setRange(0, 60)
        self.input_mi_mean.setSuffix(" s")
        self.input_mi_mean.setSingleStep(0.1)

        self.input_mi_std = QDoubleSpinBox()
        self.input_mi_std.setRange(0, 30)
        self.input_mi_std.setSuffix(" s")
        self.input_mi_std.setSingleStep(0.1)

        form_layout = QFormLayout()
        form_layout.addRow(self.tr("Protocol name"), self.input_protocol_name)
        form_layout.addRow(self.tr("Montage"), self.combo_montage)
        form_layout.addRow(self.tr("Channels"), scroll_area)
        form_layout.addRow(self.tr("Runs"), self.input_runs)

        self.btn_add_class = QPushButton("+")
        self.btn_add_class.setToolTip(self.tr("Add new class to the protocol"))
        self.btn_add_class.setFixedSize(20, 20)
        self.btn_add_class.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #28a745;
                border: none;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.btn_add_class.clicked.connect(self.add_class)

        rest_layout = QHBoxLayout()
        rest_layout.addWidget(QLabel(self.tr("Mean")))
        rest_layout.addWidget(self.input_rest_mean)
        rest_layout.addWidget(QLabel(self.tr("Std")))
        rest_layout.addWidget(self.input_rest_std)
        form_layout.addRow(self.tr("Rest time"), rest_layout)

        mi_layout = QHBoxLayout()
        mi_layout.addWidget(QLabel(self.tr("Mean")))
        mi_layout.addWidget(self.input_mi_mean)
        mi_layout.addWidget(QLabel(self.tr("Std")))
        mi_layout.addWidget(self.input_mi_std)
        form_layout.addRow(self.tr("Motor imagery time"), mi_layout)

        self.scroll_layout = QVBoxLayout()
        self.class_widgets = []

        classes_container = QWidget()
        classes_container.setLayout(self.scroll_layout)
        classes_scroll = QScrollArea()
        classes_scroll.setWidgetResizable(True)
        classes_scroll.setWidget(classes_container)

        classes_row = QHBoxLayout()
        classes_row.addWidget(QLabel(self.tr("Classes")))
        classes_row.addWidget(self.btn_add_class)
        classes_row.addStretch()

        form_layout.addRow(classes_row)
        form_layout.addRow(classes_scroll)

        self.add_class()

        layout.addLayout(form_layout)

        btn_save = QPushButton(self.tr("Save protocol"))
        btn_save.clicked.connect(self._save_protocol)
        layout.addWidget(btn_save)
        self._refresh_channels(self.combo_montage.currentText())

    def _refresh_channels(self, montage):
        montage = mne.channels.make_standard_montage(montage)

        for i in reversed(range(self.layout_channels.count())):
            widget = self.layout_channels.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.mapped_channels = {}

        for i, ch_name in enumerate(montage.ch_names):
            label = QLabel(ch_name)
            combo = QComboBox()
            combo.addItem(self.tr("Ignore"))
            combo.addItems([str(i) for i in range(32)])
            self.layout_channels.addWidget(label, i, 0)
            self.layout_channels.addWidget(combo, i, 1)
            self.mapped_channels[ch_name] = combo

    def _save_protocol(self):
        protocol_name = self.input_protocol_name.text().strip()
        if not protocol_name:
            self.toast = ToastMessage(
                self, self.tr("Protocol name cannot be empty"), WARNING_COLOR
            )
            return

        channels = {}
        for channel_name, combo in self.mapped_channels.items():
            idx = combo.currentIndex()
            if idx > 0:
                channels[channel_name] = int(combo.currentText())

        classes = {}
        for _, input_name, input_value in self.class_widgets:
            class_name = input_name.text().strip()
            if class_name:
                classes[class_name] = input_value.value()
        if not classes:
            self.toast = ToastMessage(
                self, self.tr("Add at least one class"), WARNING_COLOR
            )
            return

        protocol = {
            "name": protocol_name,
            "type": "motor_imagery",
            "montage": self.combo_montage.currentText(),
            "channels": channels,
            "runs": self.input_runs.value(),
            "classes": classes,
            "rest_time": {
                "mean": self.input_rest_mean.value(),
                "std": self.input_rest_std.value(),
            },
            "motor_imagery_time": {
                "mean": self.input_mi_mean.value(),
                "std": self.input_mi_std.value(),
            },
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

    def add_class(self):
        container = QFrame()
        layout_class = QHBoxLayout(container)

        btn_remove = QPushButton("-")
        btn_remove.setFixedSize(20, 20)
        btn_remove.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #ff0000;
                border: none;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #b30000;
            }
        """)
        btn_remove.clicked.connect(lambda: self.rmv_class(container))

        class_name = QLineEdit(self.tr("Name"))
        class_value = QSpinBox()
        class_value.setMinimum(0)
        class_value.setMaximum(99)
        class_value.setSingleStep(1)
        class_value.setValue(0)

        layout_class.addWidget(class_name)
        layout_class.addWidget(class_value)

        layout_class.addStretch()
        layout_class.addWidget(btn_remove)

        self.scroll_layout.addWidget(container)
        self.class_widgets.append((container, class_name, class_value))

    def rmv_class(self, container):
        for i, (frame, _, _) in enumerate(self.class_widgets):
            if frame == container:
                self.scroll_layout.removeWidget(frame)
                frame.deleteLater()
                self.class_widgets.pop(i)
                break
