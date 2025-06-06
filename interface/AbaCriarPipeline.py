from PyQt6.QtWidgets import (
    QWidget, QStackedWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QScrollArea, QFrame, QLabel,
)
from interface.components.NoScrollComboBox import NoScrollComboBox
from interface.components.ToastMessage import ToastMessage
import os, importlib, json

class AbaCriarPipeline(QWidget):
    def __init__(self):
        super().__init__()

        self.blocos = []

        # Layout principal
        self.layout_principal = QVBoxLayout(self)

        # Nome Pipeline

        self.nome = QFormLayout()
        self.nome.addRow('Nome do Pipeline:', QLineEdit())

        self.layout_principal.addLayout(self.nome)

        # ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        self.scroll_area.setWidget(self.scroll_content)
        self.layout_principal.addWidget(self.scroll_area)

        self.layout_botoes = QHBoxLayout()

        # Botão "+"
        self.botao_adicionar = QPushButton("+")
        self.botao_adicionar.setToolTip("Adicionar nova etapa ao pipeline")
        self.botao_adicionar.setFixedSize(20, 20)
        self.botao_adicionar.setStyleSheet("""
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
        self.botao_adicionar.clicked.connect(self.adicionar_bloco)

        # Botão salvar
        self.botao_salvar = QPushButton("Salvar pipeline")
        self.botao_salvar.clicked.connect(self.salvar_pipeline)
        self.layout_botoes.addWidget(self.botao_salvar)
        self.layout_botoes.addWidget(self.botao_adicionar)
        self.layout_principal.addLayout(self.layout_botoes)

        # Plugins disponíveis
        self.plugins = self.carregar_plugins()

    def carregar_plugins(self):
        plugins = {}
        pasta_plugins = os.path.join('functions', 'plugins')

        for nome_plugin in os.listdir(pasta_plugins):
            caminho_plugin = os.path.join(pasta_plugins, nome_plugin)
            interface_path = os.path.join(caminho_plugin, "interface.py")

            if os.path.isdir(caminho_plugin) and os.path.isfile(interface_path):
                try:
                    spec = importlib.util.spec_from_file_location(f"{nome_plugin}_interface", interface_path)
                    modulo = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(modulo)

                    # Espera que cada interface.py tenha uma classe chamada "PluginInterface"
                    classe_interface = getattr(modulo, "PluginInterface", None)
                    if classe_interface and isinstance(classe_interface, type):
                        plugins[nome_plugin] = classe_interface
                except Exception as e:
                    print(f"Erro ao carregar interface do plugin '{nome_plugin}': {e}")
        
        return plugins

    def importar_classe_dinamicamente(self, caminho, nome_classe):
        spec = importlib.util.spec_from_file_location(nome_classe, caminho)
        modulo = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(modulo)
            classe = getattr(modulo, nome_classe, None)
            if isinstance(classe, type):
                return classe
        except Exception as e:
            print(f"Erro ao importar {nome_classe}: {e}")
        return None

    def adicionar_bloco(self):
        numero_etapa = len(self.blocos) + 1

        # Container do bloco
        container = QFrame()
        layout_bloco = QVBoxLayout(container)

        # Título da etapa + botão de remover
        topo_layout = QHBoxLayout()
        titulo = QLabel(f"Etapa {numero_etapa}")
        botao_remover = QPushButton("-")
        botao_remover.setFixedSize(20, 20)
        botao_remover.setStyleSheet("""
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
        botao_remover.clicked.connect(lambda: self.remover_bloco(container))

        topo_layout.addWidget(titulo)
        topo_layout.addStretch()
        topo_layout.addWidget(botao_remover)

        layout_bloco.addLayout(topo_layout)

        # ComboBox e Stack
        combo = NoScrollComboBox()
        stack = QStackedWidget()

        for nome, classe in self.plugins.items():
            combo.addItem(nome)
            widget = classe()
            stack.addWidget(widget)

        combo.currentIndexChanged.connect(stack.setCurrentIndex)

        layout_bloco.addWidget(combo)
        layout_bloco.addWidget(stack)

        # Adiciona ao layout de scroll
        self.scroll_layout.addWidget(container)
        self.blocos.append((combo, stack, container))

        self.renumerar_blocos()

    def remover_bloco(self, container):
        # Encontra o índice do bloco com base no container
        for i, (_, _, c) in enumerate(self.blocos):
            if c == container:
                self.blocos.pop(i)
                break

        # Remove visualmente
        self.scroll_layout.removeWidget(container)
        container.setParent(None)
        container.deleteLater()

        # Renumera os blocos restantes
        self.renumerar_blocos()

    def renumerar_blocos(self):
        for i, (_, _, container) in enumerate(self.blocos):
            label = container.findChild(QLabel)
            if label:
                label.setText(f"Etapa {i+1}")

    # Dentro da classe AbaCriarPipeline

    def salvar_pipeline(self):
        nome_widget = self.nome.itemAt(0, QFormLayout.ItemRole.FieldRole).widget() # Acessa o QLineEdit corretamente
        nome_pipeline = nome_widget.text().strip()

        if not nome_pipeline:
            self.toast = ToastMessage(self, "Nome do pipeline está vazio.", color="#ff0f0f") # Exemplo de tipo de toast
            return

        dados = {
            "nome": nome_pipeline,
            "etapas": []
        }

        for combo, stack, _ in self.blocos:
            nome_plugin = combo.currentText()
            widget = stack.currentWidget() # widget é a instância da PluginInterface

            parametros = {}
            if hasattr(widget, 'get_parameters') and callable(widget.get_parameters):
                try:
                    parametros = widget.get_parameters()
                except Exception as e:
                    print(f"Erro ao obter parâmetros do plugin '{nome_plugin}': {e}")
                    self.toast = ToastMessage(self, f"Erro nos params do plugin '{nome_plugin}'. Verifique console.", color="#ff0f0f")
                    # Decide se quer continuar salvando sem os parâmetros deste plugin ou parar
                    parametros = {"erro": f"Falha ao obter parâmetros: {str(e)}"} # Ou simplesmente {}
            else:
                print(f"Aviso: Plugin '{nome_plugin}' não possui o método get_parameters().")
                self.toast = ToastMessage(self, f"Plugin '{nome_plugin}' não configurável ou antigo.", color="#bfff0f")
                # Plugin pode não ter parâmetros configuráveis ou é um tipo antigo.
            
            dados["etapas"].append({
                "plugin": nome_plugin,
                "parametros": parametros
            })

        try:
            # Garante que o diretório de pipelines exista
            diretorio_pipelines = os.path.join("data", "pipelines")
            os.makedirs(diretorio_pipelines, exist_ok=True)
            
            caminho = os.path.join(diretorio_pipelines, f"{nome_pipeline}.json")
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)

            self.toast = ToastMessage(self, "Pipeline salvo com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar arquivo do pipeline: {e}")
            self.toast = ToastMessage(self, f"Erro ao salvar pipeline: {e}", color="#ff0f0f")