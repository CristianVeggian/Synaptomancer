import os

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

FUNCTIONS_DIR = os.path.join(ROOT_DIR, "functions")
PLUGINS_DIR = os.path.join(FUNCTIONS_DIR, "plugins")

INTERFACE_DIR = os.path.join(ROOT_DIR, "interface")
TRANSLATIONS_DIR = os.path.join(ROOT_DIR, "translations")

DATA_DIR = os.path.join(ROOT_DIR, "data")
PIPELINES_DIR = os.path.join(DATA_DIR, "pipelines")
COLLECTED_DATA_DIR = os.path.join(DATA_DIR, "collected")
LOGS_DIR = os.path.join(DATA_DIR, "_logs")
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")