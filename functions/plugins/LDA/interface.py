from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox,
    QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
import json

class PluginInterface(QWidget):
    def __init__(self):
        super().__init__()

        self.is_advanced_mode = False
        self.advanced_rows = []

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # n_components
        self.label_n_components = QLabel("Nº de Componentes:")
        self.n_components_lineedit = QLineEdit()
        self.n_components_lineedit.setPlaceholderText("Ex: 1, 2 (ou deixe em branco para None)")
        form_layout.addRow(self.label_n_components, self.n_components_lineedit)

        # solver
        self.label_solver = QLabel("Solver:")
        self.solver_combobox = QComboBox()
        self.solver_combobox.addItems(["svd", "lsqr", "eigen"])
        form_layout.addRow(self.label_solver, self.solver_combobox)

        # shrinkage
        self.label_shrinkage = QLabel("Shrinkage:")
        self.shrinkage_lineedit = QLineEdit()
        self.shrinkage_lineedit.setPlaceholderText("Ex: 'auto', 0.5 (ou deixe em branco para None)")
        form_layout.addRow(self.label_shrinkage, self.shrinkage_lineedit)
        self.advanced_rows.append((self.label_shrinkage, self.shrinkage_lineedit))

        # priors
        self.label_priors = QLabel("Priors (lista de probabilidades):")
        self.priors_lineedit = QLineEdit()
        self.priors_lineedit.setPlaceholderText("Ex: [0.5, 0.5] (ou deixe em branco para None)")
        form_layout.addRow(self.label_priors, self.priors_lineedit)
        self.advanced_rows.append((self.label_priors, self.priors_lineedit))

        # store_covariance
        self.label_store_covariance = QLabel("Guardar Covariância:")
        self.store_covariance_checkbox = QCheckBox()
        self.store_covariance_checkbox.setChecked(False)
        form_layout.addRow(self.label_store_covariance, self.store_covariance_checkbox)
        self.advanced_rows.append((self.label_store_covariance, self.store_covariance_checkbox))

        # tol
        self.label_tol = QLabel("Tolerância (tol):")
        self.tol_lineedit = QLineEdit()
        self.tol_lineedit.setPlaceholderText("Ex: 0.0001")
        form_layout.addRow(self.label_tol, self.tol_lineedit)
        self.advanced_rows.append((self.label_tol, self.tol_lineedit))

        # covariance_estimator
        self.label_cov_estimator = QLabel("Estimador de Covariância:")
        self.cov_estimator_lineedit = QLineEdit()
        self.cov_estimator_lineedit.setPlaceholderText("Objeto ou deixe em branco para None")
        form_layout.addRow(self.label_cov_estimator, self.cov_estimator_lineedit)
        self.advanced_rows.append((self.label_cov_estimator, self.cov_estimator_lineedit))

        main_layout.addLayout(form_layout)

        # Botão para modo avançado
        self.toggle_advanced_button = QPushButton("Mostrar Opções Avançadas")
        self.toggle_advanced_button.clicked.connect(self._toggle_advanced_mode)
        main_layout.addWidget(self.toggle_advanced_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self._update_fields_visibility()

    def _toggle_advanced_mode(self):
        self.is_advanced_mode = not self.is_advanced_mode
        self._update_fields_visibility()

    def _update_fields_visibility(self):
        self.toggle_advanced_button.setText(
            "Ocultar Opções Avançadas" if self.is_advanced_mode else "Mostrar Opções Avançadas"
        )
        for label, widget in self.advanced_rows:
            label.setVisible(self.is_advanced_mode)
            widget.setVisible(self.is_advanced_mode)

    def get_parameters(self) -> dict:
        params = {}

        # n_components
        n_comp_text = self.n_components_lineedit.text().strip()
        params['n_components'] = int(n_comp_text) if n_comp_text else None

        # solver
        params['solver'] = self.solver_combobox.currentText()

        # shrinkage
        shrinkage_text = self.shrinkage_lineedit.text().strip()
        if not shrinkage_text:
            params['shrinkage'] = None
        elif shrinkage_text.lower() == 'auto':
            params['shrinkage'] = 'auto'
        else:
            try:
                params['shrinkage'] = float(shrinkage_text)
            except ValueError:
                params['shrinkage'] = None

        # priors
        priors_text = self.priors_lineedit.text().strip()
        if not priors_text:
            params['priors'] = None
        else:
            try:
                params['priors'] = json.loads(priors_text)
            except json.JSONDecodeError:
                params['priors'] = None

        # store_covariance
        params['store_covariance'] = self.store_covariance_checkbox.isChecked()

        # tol
        tol_text = self.tol_lineedit.text().strip()
        params['tol'] = float(tol_text) if tol_text else 0.0001

        # covariance_estimator
        cov_est_text = self.cov_estimator_lineedit.text().strip()
        params['covariance_estimator'] = None  # Simples placeholder; o objeto seria injetado via código externo.

        return params
