from PyQt6.QtWidgets import (QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog, 
                             QListWidget, QMessageBox, QLabel)
import os, shutil
from interface.translatable_widget import TranslatableWidget
from interface.components.toast_message import ToastMessage

from functions.utils.paths import PLUGINS_DIR

class MainTabPlugins(TranslatableWidget):
    def __init__(self):
        super().__init__()
        vertical_outter_layout = QVBoxLayout(self)
        horizontal_layout = QHBoxLayout()

        self.plugins_list = QListWidget()
        vertical_outter_layout.addWidget(QLabel(self.tr("Installed plugins")))

        vertical_outter_layout.addLayout(horizontal_layout)

        horizontal_layout.addWidget(self.plugins_list, stretch=3)
        
        btn_install = QPushButton(self.tr("Install new plugin"))
        btn_refresh = QPushButton(self.tr("Refresh list"))
        btn_remove = QPushButton(self.tr("Remove plugin"))

        vertical_inner_layout = QVBoxLayout()

        btn_install.clicked.connect(self._install_plugin)
        btn_refresh.clicked.connect(self._refresh_list)
        btn_remove.clicked.connect(self._remove_plugin)

        btn_install.setToolTip(self.tr("Install a new .zip plugin"))
        btn_refresh.setToolTip(self.tr("Refresh plugins list"))
        btn_remove.setToolTip(self.tr("Remove selected plugin"))

        vertical_inner_layout.addWidget(btn_install)
        vertical_inner_layout.addWidget(btn_refresh)
        vertical_inner_layout.addWidget(btn_remove)
        vertical_inner_layout.addStretch()

        horizontal_layout.addLayout(vertical_inner_layout, stretch=1)

        self._refresh_list()
    
    def _refresh_list(self):
        self.plugins_list.clear()
        for plugin in os.listdir(PLUGINS_DIR):
            if os.path.isdir(os.path.join(PLUGINS_DIR, plugin)):
                self.plugins_list.addItem(plugin)
    
    def _install_plugin(self):
        zip_file, _ = QFileDialog.getOpenFileName(
            self, self.tr("Select plugin (.zip)"), 
            "", "ZIP (*.zip)"
        )
        if zip_file:
            plugin_dir = QFileDialog.getExistingDirectory(
                self, self.tr("Destination folder"), PLUGINS_DIR
            )
            try:
                shutil.unpack_archive(zip_file, plugin_dir)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Installation failed"),
                    self.tr("Could not install plugin:\n{0}").format(str(e))
                )
                return
            ToastMessage(self, self.tr("Installed plugin: {0}").format(os.path.basename(zip_file)))
            self._refresh_list()
    
    def _remove_plugin(self):
        plugin = self.plugins_list.currentItem()
        if plugin:
            reply = QMessageBox.question(
                self,
                self.tr("Confirm"),
                self.tr("Remove {0}?").format(plugin.text())
            )
            if reply == QMessageBox.StandardButton.Yes:
                shutil.rmtree(os.path.join(PLUGINS_DIR, plugin.text()))
                ToastMessage(self, self.tr("Plugin removed!"))
                self._refresh_list()
