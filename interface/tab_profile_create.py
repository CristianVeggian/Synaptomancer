from interface.translatable_widget import TranslatableWidget
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QTextEdit, QPushButton, 
                             QFormLayout, QGridLayout)
from PyQt6.QtGui import QIntValidator, QDoubleValidator

from functions.utils.paths import PROFILES_DIR
from functions.utils.color import WARNING_COLOR, SUCCESS_COLOR
from interface.components.toast_message import ToastMessage

import datetime
import os
import json
import secrets
import string

class TabProfileCreate(TranslatableWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        
        self.form_layout = QFormLayout()

        self.input_age = QLineEdit()
        self.input_age.setPlaceholderText("25")
        self.input_age.setValidator(QIntValidator(0, 150))

        self.form_layout.addRow(QLabel(self.tr("Age (years)")), self.input_age)

        self.input_height = QLineEdit()
        self.input_height.setPlaceholderText("175")
        self.input_height.setValidator(QDoubleValidator(50.0, 250.0, 1))

        self.form_layout.addRow(QLabel(self.tr("Height (cm)")), self.input_height)

        self.input_weight = QLineEdit()
        self.input_weight.setPlaceholderText("70")
        self.input_weight.setValidator(QDoubleValidator(20.0, 300.0, 1))

        self.form_layout.addRow(QLabel(self.tr("Weight (kg)")), self.input_weight)
                
        self.sex_combo = QComboBox()
        self.sex_combo.addItem(self.tr("Male"), "male")
        self.sex_combo.addItem(self.tr("Female"), "female")
        self.sex_combo.addItem(self.tr("Intersex"), "intersex")
        self.form_layout.addRow(self.tr("Sex"), self.sex_combo)

        self.blood_type_combo = QComboBox()
        self.blood_type_combo.addItem(self.tr("A+"), "A+")
        self.blood_type_combo.addItem(self.tr("A-"), "A-")
        self.blood_type_combo.addItem(self.tr("B+"), "B+")
        self.blood_type_combo.addItem(self.tr("B-"), "B-")
        self.blood_type_combo.addItem(self.tr("AB+"), "AB+")
        self.blood_type_combo.addItem(self.tr("AB-"), "AB-")
        self.blood_type_combo.addItem(self.tr("O+"), "O+")
        self.blood_type_combo.addItem(self.tr("O-"), "O-")
        self.blood_type_combo.addItem(self.tr("Unknown"), "unknown")
        self.form_layout.addRow(self.tr("Blood Type"), self.blood_type_combo)

        self.combo_handedness = QComboBox()
        self.combo_handedness.addItem(self.tr("Right"), "right")
        self.combo_handedness.addItem(self.tr("Left"), "left")
        self.combo_handedness.addItem(self.tr("Ambidextrous"), "ambidextrous")
        self.form_layout.addRow(self.tr("Handedness"), self.combo_handedness)
        
        self.other_data_edit = QTextEdit()
        self.other_data_edit.setMaximumHeight(100)
        self.other_data_edit.setPlaceholderText(self.tr("Notes..."))
        self.form_layout.addRow(self.tr("Other data"), self.other_data_edit)
        
        self.main_layout.addLayout(self.form_layout)
        
        self.main_layout.addStretch()

        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton(self.tr("Save Profile"))
        self.save_btn.clicked.connect(self.save_profile)
        buttons_layout.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton(self.tr("Clear Form"))
        self.clear_btn.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.clear_btn)
        
        self.main_layout.addLayout(buttons_layout)

        
    def save_profile(self):
        if not self.input_age.text().strip():
            self.toast = ToastMessage(self,
                                      self.tr("Age is required!"),
                                      color=WARNING_COLOR)
            return
        
        if not self.input_height.text().strip():
            self.toast = ToastMessage(self,
                                      self.tr("Height is required!"),
                                      color=WARNING_COLOR)
            return
        
        if not self.input_weight.text().strip():
            self.toast = ToastMessage(self,
                                      self.tr("Weight is required!"),
                                      color=WARNING_COLOR)
            return
        
        if not self.sex_combo.currentData():
            self.toast = ToastMessage(self,
                                      self.tr("Sex is required!"),
                                      color=WARNING_COLOR)
            return

        if not self.blood_type_combo.currentData():
            self.toast = ToastMessage(self,
                                      self.tr("Blood Type is required!"),
                                      color=WARNING_COLOR)
            return

        if not self.combo_handedness.currentData():
            self.toast = ToastMessage(self,
                                      self.tr("Handedness is required!"),
                                      color=WARNING_COLOR)
            return

        profile_data = {
            "participant_id": self._generate_participant_id(),
            "age": int(self.input_age.text()),
            "height_cm": float(self.input_height.text()),
            "weight_kg": float(self.input_weight.text()),
            "sex": self.sex_combo.currentData(),
            "handedness": self.combo_handedness.currentData(),
            "blood_type": self.blood_type_combo.currentData(),
            "other_data": self.other_data_edit.toPlainText().strip(),
            "creation_date": datetime.datetime.now().isoformat()
        }

        profile_path = f"{PROFILES_DIR}/{profile_data['participant_id']}.json"
        
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f, indent=4)
        
        self.toast = ToastMessage(self,
                                    self.tr("Profile saved successfully as {0}!").format(profile_data['participant_id']),
                                    color=SUCCESS_COLOR
                                    )
        self.clear_form()

    def clear_form(self):
        self.input_age.clear()
        self.input_height.clear()
        self.input_weight.clear()
        self.sex_combo.setCurrentIndex(0)
        self.blood_type_combo.setCurrentIndex(0)
        self.combo_handedness.setCurrentIndex(0)
        self.other_data_edit.clear()
    
    def get_available_participant_ids(self):
        """
        Scans the participants directory and returns existing and next available IDs.

        Returns
        -------
        existing_ids : list[int]
            Sorted list of existing participant IDs.
        """

        ids = set()
        for name in os.listdir(PROFILES_DIR):
            if name.endswith(".json"):
                ids.add(os.path.splitext(name)[0])

        return ids


    def _generate_participant_id(self):
        """Generate unique ID with 10 chars (uppercase letters and digits)."""
        chars = string.ascii_uppercase + string.digits
        existing_ids = self.get_available_participant_ids()

        while True:
            candidate = ''.join(secrets.choice(chars) for _ in range(10))
            if candidate not in existing_ids:
                return candidate
