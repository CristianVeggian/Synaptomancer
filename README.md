# Synaptomancer

> Sistema de Análise Biomédica com Processamento de Sinais de Eletroencefalografia para coleta e classificação de Imagética Motora.

---

## 🔬 Contexto do Projeto

- Desenvolvido para os laboratórios Bioteca - vinculado à Universidade Tecnológica Federal do Paraná - e Laboratório de Engenharia Neural e de Reabilitação - vinculado à Universidade Estadual de Londrina.
- Uso autorizado apenas para fins acadêmicos/pesquisa nos grupos parceiros.
- Sujeito a processo de **patenteamento e futura comercialização**.

---

## 🚀 Funcionalidades

- ✅ Coleta de dados em tempo real através de comunicação serial (BCI)
- ✅ Processamento e Classificação em lote 
- ✅ Integração com sistemas Windows e Linux
- ✅ Interface gráfica simples

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia   | Versão     | Descrição                              |
|--------------|------------|----------------------------------------|
| Python       | 3.12+      | Backend e algoritmos de processamento  |
| NumPy        | 2.2.5      | Processamento numérico                 |
| scikit-learn | 1.6.1      | Algoritmos de aprendizado de máquina   |
| MNE          | 1.9.0      | Processamento e visualização de EEG    |
| BrainFlow    | 5.16.0     | Interface com placas neurofisiológicas |
| PyQt6        | 6.9.0      | Interface gráfica com Qt6              |

---

## 📦 Instalação

### Pré-requisitos

- Python 3.12+
- pip

### Passos

Clone o repositório:

```bash
git clone https://github.com/CristianVeggian/Synaptomancer.git
cd Synaptomancer
```
#### Windows

```powershell
python -m venv .venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### Linux/MacOS

```bash
python3 -m venv .venv
source venv/bin/activate
pip install -r requirements.txt
```

## ▶️ Execução 

Executar o arquivo _main.py_:
_Obs: ficar atento ao path do Python, em alguns computadores, o caminho é python3._

```
python main.py
```