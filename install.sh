#!/bin/bash
set -e

# Config
REPO_DIR=$(pwd)
USER_NAME=$SUDO_USER
if [ -z "$USER_NAME" ]; then
  USER_NAME=$(whoami)
fi

echo "============================================="
echo "   Soccer Scoreboard Installer"
echo "============================================="

# Check for Root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./install.sh)"
  exit 1
fi

# System Updates & Dependencies
echo "Updating system and installing dependencies..."
apt-get update
apt-get install -y git python3-dev python3-pip python3-setuptools build-essential \
    libgraphicsmagick++-dev libwebp-dev libopenjp2-7-dev libtiff5-dev cython3

# Python Dependencies
echo "Installing Python project requirements..."
pip3 install -r requirements.txt --break-system-packages

# 4. Install RGB Matrix Library (The tricky part)
# We check if it's already installed to save time
if python3 -c "import rgbmatrix" &> /dev/null; then
    echo "RGB Matrix library already installed."
else
    echo "Compiling and installing RGB Matrix library (This takes a few minutes)..."
    
    # Clone to a temporary folder
    cd /tmp
    rm -rf rpi-rgb-led-matrix
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
    
    # Compile and Install Python Bindings
    cd rpi-rgb-led-matrix/bindings/python
    make build-python PYTHON=$(which python3)
    make install-python PYTHON=$(which python3)
    
    # Clean up
    cd "$REPO_DIR"
    echo "RGB Matrix library installed successfully."
fi

echo "============================================="
echo "Installation Complete!"
echo "============================================="
echo "To start the scoreboard manually:"
echo "sudo python3 src/main.py"
echo "============================================="