import os


def mkdatadir():
    base = "data"
    subpastas = ["acquisitions", "protocols", "pipelines", "profiles"]

    if not os.path.exists(base):
        os.mkdir(base)

    for pasta in subpastas:
        caminho = os.path.join(base, pasta)
        if not os.path.exists(caminho):
            os.mkdir(caminho)
