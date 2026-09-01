import os
import sys

# In the portable PyInstaller build, keep mutable data and plugins next to the
# executable. In development, keep the current project-root behavior.
if getattr(sys, "frozen", False):
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LOGS_DIR = os.path.join(ROOT_DIR, "_logs")

FUNCTIONS_DIR = os.path.join(ROOT_DIR, "functions")
PLUGINS_DIR = os.path.join(FUNCTIONS_DIR, "plugins")

INTERFACE_DIR = os.path.join(ROOT_DIR, "interface")
TRANSLATIONS_DIR = os.path.join(ROOT_DIR, "translations")

DATA_DIR = os.path.join(ROOT_DIR, "data")

PIPELINES_DIR = os.path.join(DATA_DIR, "pipelines")
ACQUISITIONS_DIR = os.path.join(DATA_DIR, "acquisitions")
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
PROTOCOLS_DIR = os.path.join(DATA_DIR, "protocols")
