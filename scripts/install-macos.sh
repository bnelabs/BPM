#!/bin/bash
# BPM - macOS Native Installation Script

set -e

echo "============================================"
echo "  BPM - Blood Pressure Analysis Tool"
echo "  macOS Installation Script"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Homebrew is installed
check_homebrew() {
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}Homebrew not found. Installing...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
}

# Install Python if needed
install_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${YELLOW}Installing Python...${NC}"
        brew install python@3.11
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "Python version: $PYTHON_VERSION"
}

# Setup Python environment
setup_python_env() {
    echo ""
    echo -e "${YELLOW}Setting up Python environment...${NC}"

    # Get script directory and project root
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

    cd "$PROJECT_ROOT"

    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip

    # Install dependencies
    echo "Installing Python packages..."
    pip install -r requirements.txt

    echo -e "${GREEN}Python environment ready!${NC}"
}

# Create application bundle
create_app_bundle() {
    echo ""
    echo -e "${YELLOW}Creating application bundle...${NC}"

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

    APP_DIR="$HOME/Applications/BPM.app"
    mkdir -p "$APP_DIR/Contents/MacOS"
    mkdir -p "$APP_DIR/Contents/Resources"

    # Create Info.plist
    cat > "$APP_DIR/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>BPM</string>
    <key>CFBundleIdentifier</key>
    <string>com.bpm.bloodpressure</string>
    <key>CFBundleName</key>
    <string>BPM</string>
    <key>CFBundleDisplayName</key>
    <string>Blood Pressure Analysis</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

    # Create launcher script
    cat > "$APP_DIR/Contents/MacOS/BPM" << EOF
#!/bin/bash
cd "$PROJECT_ROOT"
source venv/bin/activate
python src/main.py
EOF

    chmod +x "$APP_DIR/Contents/MacOS/BPM"

    # Copy icon if exists
    if [ -f "$PROJECT_ROOT/resources/icons/logo.icns" ]; then
        cp "$PROJECT_ROOT/resources/icons/logo.icns" "$APP_DIR/Contents/Resources/AppIcon.icns"
    fi

    echo -e "${GREEN}Application bundle created: $APP_DIR${NC}"
}

# Create run script
create_run_script() {
    echo ""
    echo -e "${YELLOW}Creating run script...${NC}"

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

    RUN_SCRIPT="$PROJECT_ROOT/run-bpm.sh"

    cat > "$RUN_SCRIPT" << EOF
#!/bin/bash
# BPM Run Script
cd "$PROJECT_ROOT"
source venv/bin/activate
python src/main.py "\$@"
EOF

    chmod +x "$RUN_SCRIPT"

    echo -e "${GREEN}Run script created: $RUN_SCRIPT${NC}"
}

# Main installation
main() {
    echo "Starting installation..."

    check_homebrew
    install_python
    setup_python_env
    create_run_script

    echo ""
    read -p "Create Application bundle in ~/Applications? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        create_app_bundle
    fi

    echo ""
    echo "============================================"
    echo -e "${GREEN}Installation Complete!${NC}"
    echo "============================================"
    echo ""
    echo "To run BPM:"
    echo "  ./run-bpm.sh"
    echo ""
    echo "Or double-click BPM.app in ~/Applications"
    echo ""
}

main
