from interface.translatable_widget import TranslatableWidget
from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QFormLayout,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
)


class FilterConfigWidget(QGroupBox, TranslatableWidget):
    def __init__(self, parent=None):
        QGroupBox.__init__(self, parent)
        TranslatableWidget.__init__(self)

        self.setTitle(self.tr("Filter Configuration"))
        self.setVisible(False)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.combo_filter_type = QComboBox()
        self.filter_type_map = {
            "bandpass": self.tr("Band-pass"),
            "highpass": self.tr("High-pass"),
            "lowpass": self.tr("Low-pass"),
            "notch": self.tr("Notch (Band-stop)"),
        }
        for key, label in self.filter_type_map.items():
            self.combo_filter_type.addItem(label, userData=key)

        form_layout.addRow(self.tr("Filter type"), self.combo_filter_type)

        self.combo_filter_method = QComboBox()
        self.filter_method_map = {
            "butterworth": self.tr("Butterworth"),
            "chebyshev1": self.tr("Chebyshev Type I"),
            "chebyshev2": self.tr("Chebyshev Type II"),
            "bessel": self.tr("Bessel"),
        }
        for key, label in self.filter_method_map.items():
            self.combo_filter_method.addItem(label, userData=key)

        form_layout.addRow(self.tr("Filter method"), self.combo_filter_method)

        self.spin_low_cut = QDoubleSpinBox()
        self.spin_low_cut.setRange(0.1, 1000.0)
        self.spin_low_cut.setDecimals(2)
        self.spin_low_cut.setSuffix(" Hz")
        self.spin_low_cut.setValue(8.0)
        form_layout.addRow(self.tr("Low cutoff frequency"), self.spin_low_cut)

        self.spin_high_cut = QDoubleSpinBox()
        self.spin_high_cut.setRange(0.1, 1000.0)
        self.spin_high_cut.setDecimals(2)
        self.spin_high_cut.setSuffix(" Hz")
        self.spin_high_cut.setValue(30.0)
        form_layout.addRow(self.tr("High cutoff frequency"), self.spin_high_cut)

        self.combo_filter_order = QComboBox()
        for order in [2, 4, 6, 8]:
            self.combo_filter_order.addItem(str(order), userData=order)
        self.combo_filter_order.setCurrentIndex(1)  # ordem 4

        form_layout.addRow(self.tr("Filter order"), self.combo_filter_order)

        self.checkbox_zero_phase = QCheckBox(self.tr("Zero-phase filtering (filtfilt)"))
        self.checkbox_zero_phase.setChecked(True)
        form_layout.addRow("", self.checkbox_zero_phase)

        main_layout.addLayout(form_layout)

        self.combo_filter_type.currentIndexChanged.connect(self._update_visible_fields)
        self._update_visible_fields()

    def _update_visible_fields(self):
        ftype = self.combo_filter_type.currentData()

        if ftype == "highpass":
            self.spin_low_cut.setVisible(True)
            self.spin_high_cut.setVisible(False)

        elif ftype == "lowpass":
            self.spin_low_cut.setVisible(False)
            self.spin_high_cut.setVisible(True)

        else:
            self.spin_low_cut.setVisible(True)
            self.spin_high_cut.setVisible(True)

    def get_filter_config(self):
        return {
            "enabled": True,
            "type": self.combo_filter_type.currentData(),
            "method": self.combo_filter_method.currentData(),
            "lowcut": self.spin_low_cut.value(),
            "highcut": self.spin_high_cut.value(),
            "order": self.combo_filter_order.currentData(),
            "zero_phase": self.checkbox_zero_phase.isChecked(),
        }
