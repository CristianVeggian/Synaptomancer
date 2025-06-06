from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QSpinBox, QComboBox, QCheckBox,
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
        self.n_components_spinbox = QSpinBox()
        self.n_components_spinbox.setMinimum(1)
        self.n_components_spinbox.setValue(4)
        form_layout.addRow(self.label_n_components, self.n_components_spinbox)

        # reg
        self.label_reg = QLabel("Regularização (reg):")
        self.reg_lineedit = QLineEdit()
        self.reg_lineedit.setPlaceholderText("Ex: 0.01, 'ledoit_wolf', 'oas' (ou deixe em branco para None)")
        form_layout.addRow(self.label_reg, self.reg_lineedit)
        self.advanced_rows.append((self.label_reg, self.reg_lineedit))

        # log
        self.label_log = QLabel("Log-variância (log):")
        self.log_combobox = QComboBox()
        self.log_combobox.addItems(["Automático (None)", "Sim (True)", "Não (False)"])
        form_layout.addRow(self.label_log, self.log_combobox)
        self.advanced_rows.append((self.label_log, self.log_combobox))

        # cov_est
        self.label_cov_est = QLabel("Estimador de Covariância (cov_est):")
        self.cov_est_combobox = QComboBox()
        self.cov_est_combobox.addItems(["concat", "epoch"])
        form_layout.addRow(self.label_cov_est, self.cov_est_combobox)
        self.advanced_rows.append((self.label_cov_est, self.cov_est_combobox))

        # transform_into
        self.label_transform_into = QLabel("Transformar Para (transform_into):")
        self.transform_into_combobox = QComboBox()
        self.transform_into_combobox.addItems(["average_power", "csp_space"])
        form_layout.addRow(self.label_transform_into, self.transform_into_combobox)
        self.advanced_rows.append((self.label_transform_into, self.transform_into_combobox))

        # norm_trace
        self.label_norm_trace = QLabel("Normalizar Traço (norm_trace):")
        self.norm_trace_checkbox = QCheckBox()
        self.norm_trace_checkbox.setChecked(False)
        form_layout.addRow(self.label_norm_trace, self.norm_trace_checkbox)
        self.advanced_rows.append((self.label_norm_trace, self.norm_trace_checkbox))

        # cov_method_params
        self.label_cov_method_params = QLabel("Parâmetros Covariância (cov_method_params):")
        self.cov_method_params_lineedit = QLineEdit()
        self.cov_method_params_lineedit.setPlaceholderText("Ex: {\"method\": \"auto\"} (ou deixe em branco para None)")
        form_layout.addRow(self.label_cov_method_params, self.cov_method_params_lineedit)
        self.advanced_rows.append((self.label_cov_method_params, self.cov_method_params_lineedit))

        # rank
        self.label_rank = QLabel("Rank (PCA):")
        self.rank_lineedit = QLineEdit()
        self.rank_lineedit.setPlaceholderText("Ex: 5, 'auto' (ou deixe em branco para None)")
        form_layout.addRow(self.label_rank, self.rank_lineedit)
        self.advanced_rows.append((self.label_rank, self.rank_lineedit))

        # component_order
        self.label_component_order = QLabel("Ordem dos Componentes (component_order):")
        self.component_order_combobox = QComboBox()
        self.component_order_combobox.addItems(["mutual_info", "alternate"])  # Atualizado para "alternate"
        form_layout.addRow(self.label_component_order, self.component_order_combobox)
        self.advanced_rows.append((self.label_component_order, self.component_order_combobox))

        main_layout.addLayout(form_layout)

        self.toggle_advanced_button = QPushButton("Mostrar Opções Avançadas")
        self.toggle_advanced_button.setCheckable(False)
        self.toggle_advanced_button.clicked.connect(self._toggle_advanced_mode)
        main_layout.addWidget(self.toggle_advanced_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self._update_fields_visibility()

    def _toggle_advanced_mode(self):
        self.is_advanced_mode = not self.is_advanced_mode
        self._update_fields_visibility()

    def _update_fields_visibility(self):
        if self.is_advanced_mode:
            self.toggle_advanced_button.setText("Ocultar Opções Avançadas")
            for label, field_widget in self.advanced_rows:
                label.setVisible(True)
                field_widget.setVisible(True)
        else:
            self.toggle_advanced_button.setText("Mostrar Opções Avançadas")
            for label, field_widget in self.advanced_rows:
                label.setVisible(False)
                field_widget.setVisible(False)

    def get_parameters(self) -> dict:
        params = {}
        params['n_components'] = self.n_components_spinbox.value()

        # Se o modo avançado estiver ativo ou os campos avançados estiverem visíveis:
        if self.is_advanced_mode or self.reg_lineedit.isVisible():
            reg_text = self.reg_lineedit.text().strip()
            if not reg_text:
                params['reg'] = None
            else:
                try:
                    params['reg'] = float(reg_text)
                except ValueError:
                    params['reg'] = reg_text

            log_choice = self.log_combobox.currentText()
            if log_choice == "Automático (None)":
                params['log'] = None
            elif log_choice == "Sim (True)":
                params['log'] = True
            else:
                params['log'] = False

            params['cov_est'] = self.cov_est_combobox.currentText()
            params['transform_into'] = self.transform_into_combobox.currentText()
            params['norm_trace'] = self.norm_trace_checkbox.isChecked()

            cov_params_text = self.cov_method_params_lineedit.text().strip()
            if not cov_params_text:
                params['cov_method_params'] = None
            else:
                try:
                    params['cov_method_params'] = json.loads(cov_params_text)
                except json.JSONDecodeError:
                    params['cov_method_params'] = None

            rank_text = self.rank_lineedit.text().strip()
            if not rank_text:
                params['rank'] = None
            else:
                if rank_text.lower() == 'auto':
                    params['rank'] = 'auto'
                else:
                    try:
                        params['rank'] = int(rank_text)
                    except ValueError:
                        params['rank'] = None

            params['component_order'] = self.component_order_combobox.currentText()
        else:
            # Valores padrão (correspondentes às especificações do MNE)
            params['reg'] = None
            params['log'] = None  # Padrão se transform_into for 'average_power'
            params['cov_est'] = 'concat'
            params['transform_into'] = 'average_power'
            params['norm_trace'] = False
            params['cov_method_params'] = None
            params['rank'] = None
            params['component_order'] = 'mutual_info'
            
        return params