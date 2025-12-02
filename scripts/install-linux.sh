#!/bin/bash
# BPM - Linux Native Installation Script
# Supports: Ubuntu/Debian, Fedora/RHEL, Arch Linux

set -e

echo "============================================"
echo "  BPM - Blood Pressure Analysis Tool"
echo "  Linux Installation Script"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run as root. The script will ask for sudo when needed.${NC}"
    exit 1
fi

# Detect distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_FAMILY=$ID_LIKE
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        DISTRO=$DISTRIB_ID
    else
        DISTRO=$(uname -s)
    fi
    echo "Detected: $DISTRO"
}

# Install system dependencies based on distro
install_system_deps() {
    echo ""
    echo -e "${YELLOW}Installing system dependencies...${NC}"

    case $DISTRO in
        ubuntu|debian|linuxmint|pop)
            sudo apt-get update
            sudo apt-get install -y \
                python3 \
                python3-pip \
                python3-venv \
                libgl1-mesa-glx \
                libglib2.0-0 \
                libfontconfig1 \
                libxkbcommon0 \
                libxkbcommon-x11-0 \
                libdbus-1-3 \
                libegl1 \
                libxcb-cursor0 \
                libxcb-icccm4 \
                libxcb-keysyms1 \
                libxcb-shape0 \
                fonts-ubuntu \
                fonts-liberation
            ;;
        fedora|rhel|centos|rocky|alma)
            sudo dnf install -y \
                python3 \
                python3-pip \
                mesa-libGL \
                glib2 \
                fontconfig \
                libxkbcommon \
                libxkbcommon-x11 \
                dbus-libs \
                libglvnd-egl \
                xcb-util-cursor \
                xcb-util-keysyms \
                google-noto-sans-fonts \
                liberation-fonts
            ;;
        arch|manjaro|endeavouros)
            sudo pacman -Sy --noconfirm \
                python \
                python-pip \
                mesa \
                glib2 \
                fontconfig \
                libxkbcommon \
                libxkbcommon-x11 \
                dbus \
                libglvnd \
                xcb-util-cursor \
                xcb-util-keysyms \
                ttf-ubuntu-font-family \
                ttf-liberation
            ;;
        opensuse*|suse*)
            sudo zypper install -y \
                python3 \
                python3-pip \
                Mesa-libGL1 \
                libglib-2_0-0 \
                fontconfig \
                libxkbcommon0 \
                libxkbcommon-x11-0 \
                libdbus-1-3 \
                libglvnd \
                liberation-fonts
            ;;
        *)
            echo -e "${YELLOW}Unknown distribution. Please install Qt6 dependencies manually.${NC}"
            echo "Required: Python 3.10+, Qt6/PySide6 system libraries"
            ;;
    esac
}

# Create virtual environment and install Python packages
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

# Create desktop entry
create_desktop_entry() {
    echo ""
    echo -e "${YELLOW}Creating desktop entry...${NC}"

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

    DESKTOP_FILE="$HOME/.local/share/applications/bpm.desktop"
    mkdir -p "$HOME/.local/share/applications"

    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=BPM
GenericName=Blood Pressure Analysis
Comment=Analyze blood pressure variability patterns
Exec=bash -c 'cd "$PROJECT_ROOT" && source venv/bin/activate && python src/main.py'
Icon=$PROJECT_ROOT/resources/icons/logo.png
Terminal=false
Categories=Science;Medical;
Keywords=blood;pressure;medical;health;analysis;
StartupNotify=true
EOF

    chmod +x "$DESKTOP_FILE"

    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    fi

    echo -e "${GREEN}Desktop entry created!${NC}"
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

    detect_distro
    install_system_deps
    setup_python_env
    create_run_script

    echo ""
    read -p "Create desktop shortcut? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        create_desktop_entry
    fi

    echo ""
    echo "============================================"
    echo -e "${GREEN}Installation Complete!${NC}"
    echo "============================================"
    echo ""
    echo "To run BPM:"
    echo "  ./run-bpm.sh"
    echo ""
    echo "Or from the application menu (if desktop entry was created)"
    echo ""
}

main
