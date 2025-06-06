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

```bash
git clone git@github.com:usuario/projeto.git
cd projeto
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
