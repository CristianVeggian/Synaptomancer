import os

def mkdatadir():
    base = "data"
    subpastas = ["collected", "pipelines", "profiles"]

    # Cria a pasta 'data' se não existir
    if not os.path.exists(base):
        os.mkdir(base)

    # Cria as subpastas, se não existirem
    for pasta in subpastas:
        caminho = os.path.join(base, pasta)
        if not os.path.exists(caminho):
            os.mkdir(caminho)
