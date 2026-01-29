from interface.translatable_widget import TranslatableWidget
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QComboBox

from functions.utils.paths import PROFILES_DIR
from functions.utils.i18n import PROFILE_FIELDS
from interface.components.stats_chart import StatsChart
from collections import Counter

import os
import json

class TabProfileView(TranslatableWidget):
    def __init__(self):
        super().__init__()
        
        self.layout_main = QHBoxLayout(self)

        self.layout_left = QVBoxLayout()
        self.layout_right = QVBoxLayout()

        self.profiles_count_label = QLabel()

        title = QLabel(self.tr("Registered profiles"))

        self.layout_left.addWidget(title)
        self.layout_left.addWidget(self.profiles_count_label)
        self.layout_left.addStretch()

        self.FEATURE_KEYS = {
            "age": self.tr("Age"),
            "height_cm": self.tr("Height"),
            "weight_kg": self.tr("Weight"),
            "sex": self.tr("Sex"),
            "blood_type": self.tr("Blood Type"),
            "handedness": self.tr("Handedness"),
        }

        self.combo_feature = QComboBox()
        
        for key, label in self.FEATURE_KEYS.items():
            self.combo_feature.addItem(
                self.tr(label),
                key
            )

        self.layout_right.addWidget(QLabel(self.tr("Select feature to view")))
        self.layout_right.addWidget(self.combo_feature)

        self.layout_main.addLayout(self.layout_left, stretch=1)
        self.layout_main.addLayout(self.layout_right, stretch=3)
        self._populate_profile_view()

        self.chart = StatsChart()
        self.layout_right.addWidget(self.chart)

        self.combo_feature.currentTextChanged.connect(
            self._render_dashboard
        )

    def showEvent(self, event):
        self._populate_profile_view()
        self._render_dashboard()
        super().showEvent(event)
    
    def _load_profiles(self):
        profiles = []

        for file in os.listdir(PROFILES_DIR):
            if file.endswith(".json"):
                with open(os.path.join(PROFILES_DIR, file), "r", encoding="utf-8") as f:
                    profiles.append(json.load(f))

        return profiles

    def _populate_profile_view(self):

        profiles = self._load_profiles()
        
        self.profiles_count_label.setText(
            str(len(profiles))
        )

    def _compute_distribution(self, field):
        profiles = self._load_profiles()
        values = [p.get(field) for p in profiles if p.get(field)]

        return Counter(values)

    def _render_dashboard(self):
        field = self.combo_feature.currentData()
        field_type = PROFILE_FIELDS[field]["type"]
        field_label = self.tr(PROFILE_FIELDS[field]["label"])

        if not field:
            self.chart.clear()
            return

        dist = self._compute_distribution(field)

        if not dist:
            self.chart.clear()
            return

        labels = list(dist.keys())
        values = list(dist.values())

        if field_type == "categorical":
            self.chart.plot_pie(labels, values, title=field_label)
        else:
            self.chart.plot_bar(labels, values, title=field_label)