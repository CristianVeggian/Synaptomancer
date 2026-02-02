from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QComboBox,
    QLabel,
    QCheckBox,
    QDialogButtonBox,
)

from PyQt6.QtCore import QSettings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Settings"))
        self.setModal(False)
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en_US")
        self.language_combo.addItem("Português", "pt_BR")

        layout.addWidget(QLabel(self.tr("Language")))
        layout.addWidget(self.language_combo)

        # Save state
        self.save_state_checkbox = QCheckBox(self.tr("Save application state on exit"))
        layout.addWidget(self.save_state_checkbox)

        layout.addStretch()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Close
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.close)

        layout.addWidget(buttons)

    def save_settings(self):
        settings = QSettings("Synaptomancer", "SynaptomancerApp")
        settings.setValue("language", self.language_combo.currentData())
        settings.setValue("save_state", self.save_state_checkbox.isChecked())
