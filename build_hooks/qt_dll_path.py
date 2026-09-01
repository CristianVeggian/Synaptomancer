"""Ensure the bundled Qt DLLs take precedence over any system Qt installation."""

import os
import sys


if getattr(sys, "frozen", False) and sys.platform == "win32":
    qt_bin_dir = os.path.join(sys._MEIPASS, "PyQt6", "Qt6", "bin")
    if os.path.isdir(qt_bin_dir):
        # add_dll_directory affects native extension loading on modern Windows;
        # PATH also covers dependencies loaded later by Qt itself.
        os.add_dll_directory(qt_bin_dir)
        os.environ["PATH"] = qt_bin_dir + os.pathsep + os.environ.get("PATH", "")
