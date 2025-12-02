#!/usr/bin/env python3
"""
BPM - Blood Pressure Monitoring Analysis Tool

A clinical decision-support tool for analyzing temporal blood pressure variability.

Usage:
    python main.py

Or after building:
    ./BPM (macOS/Linux)
    BPM.exe (Windows)
"""

import sys
import os
import platform
from pathlib import Path

# Ensure src directory is in path for imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QFont, QFontDatabase, QIcon

from ui.main_window import MainWindow


def get_system_font() -> str:
    """Get appropriate system font for current platform"""
    system = platform.system()

    if system == "Darwin":  # macOS
        return "SF Pro Display, Helvetica Neue, Helvetica"
    elif system == "Windows":
        return "Segoe UI, Arial"
    else:  # Linux and others
        return "Ubuntu, Cantarell, DejaVu Sans, Liberation Sans, sans-serif"


def setup_environment():
    """Setup environment variables for proper rendering"""
    system = platform.system()

    if system == "Linux":
        # Fix for some Linux distributions with Qt
        if "QT_QPA_PLATFORM" not in os.environ:
            # Try xcb first, fall back to wayland if needed
            os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

        # Fix for font rendering on Linux
        os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

        # Fix for some GTK theme issues
        os.environ.setdefault("QT_QPA_PLATFORMTHEME", "gtk3")


def main():
    """Application entry point"""
    # Setup environment before creating QApplication
    setup_environment()

    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # Set application info
    app.setApplicationName("BPM")
    app.setApplicationDisplayName("Blood Pressure Analysis")
    app.setOrganizationName("BPM")
    app.setApplicationVersion("1.0.0")

    # Set application icon
    icon_path = Path(__file__).parent.parent / "resources" / "icons" / "logo.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Set locale for proper number formatting (Turkish default: comma decimal, dot thousands)
    QLocale.setDefault(QLocale(QLocale.Turkish, QLocale.Turkey))

    # Set default font based on platform
    font = QFont()
    font.setFamily(get_system_font())
    font.setPointSize(11 if platform.system() == "Linux" else 13)
    app.setFont(font)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
