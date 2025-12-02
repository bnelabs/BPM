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
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.main_window import MainWindow


def main():
    """Application entry point"""
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

    # Set default font
    font = QFont()
    font.setFamily("-apple-system, BlinkMacSystemFont, SF Pro Display, Segoe UI, Roboto")
    font.setPointSize(13)
    app.setFont(font)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
