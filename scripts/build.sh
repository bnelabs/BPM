#!/bin/bash
# BPM Build Script - Cross-platform (Linux/macOS)
# Run this script to create a standalone executable

set -e

echo "========================================"
echo "  BPM Build Script"
echo "========================================"
echo ""

# Get project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Parse arguments
CLEAN=false
SKIP_VENV=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN=true
            shift
            ;;
        --skip-venv)
            SKIP_VENV=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Clean previous builds
if [ "$CLEAN" = true ]; then
    echo "[1/5] Cleaning previous builds..."
    rm -rf build dist *.spec.bak
else
    echo "[1/5] Skipping clean (use --clean to remove previous builds)"
fi

# Setup virtual environment
if [ "$SKIP_VENV" = false ]; then
    echo "[2/5] Setting up virtual environment..."

    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    # Activate venv
    source venv/bin/activate

    echo "[3/5] Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller
else
    echo "[2/5] Skipping venv setup"
    echo "[3/5] Skipping dependency install"
fi

# Build with PyInstaller
echo "[4/5] Building executable with PyInstaller..."
pyinstaller BPM.spec --noconfirm

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Linux*)     PLATFORM="Linux" ;;
    Darwin*)    PLATFORM="macOS" ;;
    *)          PLATFORM="Unknown" ;;
esac

# Check result
if [ "$PLATFORM" = "macOS" ] && [ -d "dist/BPM.app" ]; then
    echo ""
    echo "========================================"
    echo "  BUILD SUCCESSFUL!"
    echo "========================================"
    echo ""
    echo "Application bundle created at:"
    echo "  dist/BPM.app"
    echo ""

    echo "[5/5] Creating distribution package..."

    VERSION="1.0.0"
    DMG_NAME="BPM-macOS-$VERSION.dmg"

    # Create a simple DMG
    if command -v hdiutil &> /dev/null; then
        hdiutil create -volname "BPM" -srcfolder "dist/BPM.app" -ov -format UDZO "dist/$DMG_NAME"
        echo "Distribution package created:"
        echo "  dist/$DMG_NAME"
    else
        # Fallback to zip
        cd dist && zip -r "BPM-macOS-$VERSION.zip" BPM.app && cd ..
        echo "Distribution package created:"
        echo "  dist/BPM-macOS-$VERSION.zip"
    fi

elif [ -f "dist/BPM" ]; then
    echo ""
    echo "========================================"
    echo "  BUILD SUCCESSFUL!"
    echo "========================================"
    echo ""
    echo "Executable created at:"
    echo "  dist/BPM"
    echo ""

    # Get file size
    SIZE=$(du -h "dist/BPM" | cut -f1)
    echo "File size: $SIZE"

    echo "[5/5] Creating distribution package..."

    VERSION="1.0.0"

    # Create AppImage for Linux
    if [ "$PLATFORM" = "Linux" ]; then
        # Simple tar.gz package
        cd dist
        tar -czvf "BPM-Linux-$VERSION.tar.gz" BPM
        cd ..
        echo "Distribution package created:"
        echo "  dist/BPM-Linux-$VERSION.tar.gz"
    fi

else
    echo ""
    echo "========================================"
    echo "  BUILD FAILED!"
    echo "========================================"
    echo ""
    echo "Check the error messages above for details."
    exit 1
fi

echo ""
echo "Done!"
