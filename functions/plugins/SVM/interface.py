from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QPushButton
)
from PyQt6.QtCore import Qt

class PluginInterface(QWidget):
    def __init__(self):
        super().__init__()

        self.is_advanced_mode = False
        self.advanced_rows = []

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # C (float > 0)
        self.label_c = QLabel("Parâmetro C:")
        self.spin_c = QDoubleSpinBox()
        self.spin_c.setMinimum(0.001)
        self.spin_c.setMaximum(10000.0)
        self.spin_c.setValue(1.0)
        form_layout.addRow(self.label_c, self.spin_c)

        # Kernel
        self.label_kernel = QLabel("Kernel:")
        self.combo_kernel = QComboBox()
        self.combo_kernel.addItems(['linear', 'poly', 'rbf', 'sigmoid', 'precomputed'])
        form_layout.addRow(self.label_kernel, self.combo_kernel)

        # Degree
        self.label_degree = QLabel("Grau (degree):")
        self.spin_degree = QSpinBox()
        self.spin_degree.setMinimum(0)
        self.spin_degree.setValue(3)
        form_layout.addRow(self.label_degree, self.spin_degree)
        self.advanced_rows.append((self.label_degree, self.spin_degree))

        # Gamma
        self.label_gamma = QLabel("Gamma:")
        self.combo_gamma = QComboBox()
        self.combo_gamma.addItems(["scale", "auto"])
        form_layout.addRow(self.label_gamma, self.combo_gamma)

        # Coef0
        self.label_coef0 = QLabel("Coef0:")
        self.spin_coef0 = QDoubleSpinBox()
        self.spin_coef0.setValue(0.0)
        form_layout.addRow(self.label_coef0, self.spin_coef0)
        self.advanced_rows.append((self.label_coef0, self.spin_coef0))

        # Shrinking
        self.label_shrinking = QLabel("Shrinking:")
        self.check_shrinking = QCheckBox()
        self.check_shrinking.setChecked(True)
        form_layout.addRow(self.label_shrinking, self.check_shrinking)

        # Probability
        self.label_prob = QLabel("Estimativa de Probabilidade:")
        self.check_prob = QCheckBox()
        self.check_prob.setChecked(False)
        form_layout.addRow(self.label_prob, self.check_prob)

        # Tolerance
        self.label_tol = QLabel("Tolerância (tol):")
        self.spin_tol = QDoubleSpinBox()
        self.spin_tol.setDecimals(6)
        self.spin_tol.setSingleStep(0.001)
        self.spin_tol.setValue(0.001)
        form_layout.addRow(self.label_tol, self.spin_tol)

        # Cache Size
        self.label_cache = QLabel("Cache (MB):")
        self.spin_cache = QDoubleSpinBox()
        self.spin_cache.setValue(200.0)
        form_layout.addRow(self.label_cache, self.spin_cache)
        self.advanced_rows.append((self.label_cache, self.spin_cache))

        # Class weight
        self.label_class_weight = QLabel("Peso das Classes:")
        self.combo_class_weight = QComboBox()
        self.combo_class_weight.addItems(["None", "balanced"])
        form_layout.addRow(self.label_class_weight, self.combo_class_weight)
        self.advanced_rows.append((self.label_class_weight, self.combo_class_weight))

        # Verbose
        self.label_verbose = QLabel("Verbose:")
        self.check_verbose = QCheckBox()
        form_layout.addRow(self.label_verbose, self.check_verbose)
        self.advanced_rows.append((self.label_verbose, self.check_verbose))

        # Max Iter
        self.label_max_iter = QLabel("Máx. Iterações:")
        self.spin_max_iter = QSpinBox()
        self.spin_max_iter.setRange(-1, 1_000_000)
        self.spin_max_iter.setValue(-1)
        form_layout.addRow(self.label_max_iter, self.spin_max_iter)
        self.advanced_rows.append((self.label_max_iter, self.spin_max_iter))

        # Decision function shape
        self.label_decision = QLabel("Forma função de decisão:")
        self.combo_decision = QComboBox()
        self.combo_decision.addItems(["ovr", "ovo"])
        form_layout.addRow(self.label_decision, self.combo_decision)

        # Break ties
        self.label_break = QLabel("Quebrar Empates (break_ties):")
        self.check_break = QCheckBox()
        form_layout.addRow(self.label_break, self.check_break)
        self.advanced_rows.append((self.label_break, self.check_break))

        # Random state
        self.label_random = QLabel("Random State:")
        self.line_random = QLineEdit()
        self.line_random.setPlaceholderText("Ex: 42 (ou deixe em branco para None)")
        form_layout.addRow(self.label_random, self.line_random)
        self.advanced_rows.append((self.label_random, self.line_random))

        layout.addLayout(form_layout)

        # Botão de alternância
        self.botao_toggle = QPushButton("Mostrar Opções Avançadas")
        self.botao_toggle.clicked.connect(self._toggle_advanced_mode)
        layout.addWidget(self.botao_toggle, alignment=Qt.AlignmentFlag.AlignLeft)

        self._update_fields_visibility()

    def _toggle_advanced_mode(self):
        self.is_advanced_mode = not self.is_advanced_mode
        self._update_fields_visibility()

    def _update_fields_visibility(self):
        if self.is_advanced_mode:
            self.botao_toggle.setText("Ocultar Opções Avançadas")
            for label, widget in self.advanced_rows:
                label.setVisible(True)
                widget.setVisible(True)
        else:
            self.botao_toggle.setText("Mostrar Opções Avançadas")
            for label, widget in self.advanced_rows:
                label.setVisible(False)
                widget.setVisible(False)

    def get_parameters(self) -> dict:
        params = {
            "C": self.spin_c.value(),
            "kernel": self.combo_kernel.currentText(),
            "degree": self.spin_degree.value(),
            "gamma": self.combo_gamma.currentText(),
            "coef0": self.spin_coef0.value(),
            "shrinking": self.check_shrinking.isChecked(),
            "probability": self.check_prob.isChecked(),
            "tol": self.spin_tol.value(),
            "cache_size": self.spin_cache.value(),
            "class_weight": None if self.combo_class_weight.currentText() == "None" else "balanced",
            "verbose": self.check_verbose.isChecked(),
            "max_iter": self.spin_max_iter.value(),
            "decision_function_shape": self.combo_decision.currentText(),
            "break_ties": self.check_break.isChecked(),
        }

        random_state_text = self.line_random.text().strip()
        if not random_state_text:
            params["random_state"] = None
        else:
            try:
                params["random_state"] = int(random_state_text)
            except ValueError:
                params["random_state"] = None  # Ou lançar erro

        return params
