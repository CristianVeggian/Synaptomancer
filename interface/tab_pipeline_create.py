from PyQt6.QtWidgets import ( QWidget,
    QStackedWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QScrollArea, QFrame, QLabel,
)

from functions.utils.paths import PLUGINS_DIR, PIPELINES_DIR
from functions.utils.color import WARNING_COLOR, ERROR_COLOR

from interface.translatable_widget import TranslatableWidget
from interface.components.no_scroll_combobox import NoScrollComboBox
from interface.components.toast_message import ToastMessage
import os, importlib, json

class TabPipelineCreate(TranslatableWidget):
    def __init__(self):
        super().__init__()

        self.steps = []

        self.main_layout = QVBoxLayout(self)

        self.name = QFormLayout()
        self.name.addRow(
            self.tr("Pipeline name"),
            QLineEdit()
        )

        self.main_layout.addLayout(self.name)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        self.buttons_layout = QHBoxLayout()

        self.btn_add = QPushButton("+")
        self.btn_add.setToolTip(self.tr("Add new step to the pipeline"))
        self.btn_add.setFixedSize(20, 20)
        self.btn_add.setStyleSheet("""
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
        self.btn_add.clicked.connect(self._add_step)

        self.btn_save = QPushButton(self.tr("Save pipeline"))
        self.btn_save.clicked.connect(self._save_pipeline)
        self.buttons_layout.addWidget(self.btn_save)
        self.buttons_layout.addWidget(self.btn_add)
        self.main_layout.addLayout(self.buttons_layout)

        self.plugins = self._load_plugins()

    def _load_plugins(self):
        plugins = {}

        for plugin_name in os.listdir(PLUGINS_DIR):
            plugin_path = os.path.join(PLUGINS_DIR, plugin_name)
            interface_path = os.path.join(plugin_path, "interface.py")

            if os.path.isdir(plugin_path) and os.path.isfile(interface_path):
                try:
                    spec = importlib.util.spec_from_file_location(f"{plugin_name}_interface", interface_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    interface_class = getattr(module, "PluginInterface", None)
                    if interface_class and isinstance(interface_class, type):
                        plugins[plugin_name] = interface_class
                except Exception as e:
                    self.toast = ToastMessage(
                        self,
                        self.tr("One or more plugins could not be loaded."),
                        color=WARNING_COLOR
                    )

        return plugins

    def _add_step(self):
        step_number = len(self.steps) + 1

        container = QFrame()
        step_layout = QVBoxLayout(container)

        upper_layout = QHBoxLayout()
        title = QLabel(
            self.tr("Stage {0}").format(step_number)
            )
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
        btn_remove.clicked.connect(lambda: self._remove_step(container))

        upper_layout.addWidget(title)
        upper_layout.addStretch()
        upper_layout.addWidget(btn_remove)

        step_layout.addLayout(upper_layout)

        combo = NoScrollComboBox()
        stack = QStackedWidget()

        for name, classe in self.plugins.items():
            combo.addItem(name)
            widget = classe()
            stack.addWidget(widget)

        combo.currentIndexChanged.connect(stack.setCurrentIndex)

        step_layout.addWidget(combo)
        step_layout.addWidget(stack)

        self.scroll_layout.addWidget(container)
        self.steps.append((combo, stack, container))

        self._enumerate_steps()

    def _remove_step(self, container):
        for i, (_, _, c) in enumerate(self.steps):
            if c == container:
                self.steps.pop(i)
                break

        self.scroll_layout.removeWidget(container)
        container.setParent(None)
        container.deleteLater()

        self._enumerate_steps()

    def _enumerate_steps(self):
        for i, (_, _, container) in enumerate(self.steps):
            label = container.findChild(QLabel)
            if label:
                label.setText(
                    self.tr("Stage {0}").format(i + 1)
                )

    def _save_pipeline(self):
        widget_name = self.name.itemAt(0, QFormLayout.ItemRole.FieldRole).widget()
        pipeline_name = widget_name.text().strip()

        if not pipeline_name:
            self.toast = ToastMessage(
                self,
                self.tr("Pipeline name is empty"),
                color=ERROR_COLOR)
            return

        pipeline_data = {
            "name": pipeline_name,
            "steps": []
        }

        for combo, stack, _ in self.steps:
            plugin_name = combo.currentText()
            widget = stack.currentWidget()

            parameters = {}
            if hasattr(widget, 'get_parameters') and callable(widget.get_parameters):
                try:
                    parameters = widget.get_parameters()
                except Exception as e:
                    self.toast = ToastMessage(
                        self,
                        self.tr("Plugin '{0}' parameters error: {1}").format(plugin_name, str(e)),
                        color=ERROR_COLOR
                        )
            else:
                self.toast = ToastMessage(
                    self,
                    self.tr("Plugin '{0}' is not configurable or old.").format(plugin_name),
                    color=WARNING_COLOR
                    )
            
            pipeline_data["steps"].append({
                "plugin": plugin_name,
                "parameters": parameters
            })

        try:
            destination_path = os.path.join(PIPELINES_DIR, f"{pipeline_name}.json")
            with open(destination_path, "w", encoding="utf-8") as f:
                json.dump(pipeline_data, f, indent=4, ensure_ascii=False)

            self.toast = ToastMessage(
                self,
                self.tr("Pipeline saved successfully!")
                )
        except Exception as e:
            self.toast = ToastMessage(
                self,
                self.tr("Error saving pipeline: {0}").format(e),
                color=ERROR_COLOR
                )