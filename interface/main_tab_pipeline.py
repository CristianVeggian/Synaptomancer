from PyQt6.QtWidgets import QTabWidget, QVBoxLayout
from interface.translatable_widget import TranslatableWidget
from interface.tab_pipeline_execute import TabPipelineExecute
from interface.tab_pipeline_create import TabPipelineCreate


class MainTabPipeline(TranslatableWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.tab_execute_pipeline = TabPipelineExecute()
        self.tab_create_pipeline = TabPipelineCreate()

        self.tabs.addTab(self.tab_execute_pipeline, self.tr("Execute Pipeline"))
        self.tabs.addTab(self.tab_create_pipeline, self.tr("Create Pipeline"))

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
