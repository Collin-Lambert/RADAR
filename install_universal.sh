#!/bin/bash

if [[ "$(uname)" == "Darwin" ]]; then
    echo "Running on macOS"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
            echo "Homebrew not found. Please install Homebrew first: https://brew.sh"
            exit 1
    fi

    # Install GNU Radio using Homebrew
    brew install gnuradio

    ZSHRC="$HOME/.zshrc"

    # Lines to add
    PYTHONPATH_LINE='export PYTHONPATH=/opt/homebrew/Cellar/gnuradio/3.10.12.0/lib/python3.13/site-packages:$PYTHONPATH'
    LD_LIBRARY_PATH_LINE='export LD_LIBRARY_PATH=/opt/homebrew/Cellar/gnuradio/3.10.12.0/lib:$LD_LIBRARY_PATH'

    # Append if not already present
    grep -qxF "$PYTHONPATH_LINE" "$ZSHRC" || echo "$PYTHONPATH_LINE" >> "$ZSHRC"
    grep -qxF "$LD_LIBRARY_PATH_LINE" "$ZSHRC" || echo "$LD_LIBRARY_PATH_LINE" >> "$ZSHRC"

    echo "Environment variables added to ~/.zshrc"

    brew install soapysdr

    # Ensure pip is installed
    if ! command -v pip3 &> /dev/null; then
        echo "pip3 not found, installing..."
        brew install python
    else
        echo "pip3 is already installed."
    fi


elif [[ "$(uname)" == "Linux" ]]; then
    echo "Running on Linux"

    # Install GNU Radio
    sudo apt install -y gnuradio

    # Ensure pip is installed
    if ! command -v pip3 &> /dev/null; then
        echo "pip3 not found, installing..."
        sudo apt install -y python3-pip
    else
        echo "pip3 is already installed."
    fi

else
    echo "Unknown OS: $(uname)"
fi

# Upgrade pip (optional but good practice)
python3 -m pip install --upgrade pip



# Create virtual environment
python3 -m venv venv --system-site-packages

# Enter venv
source venv/bin/activate

pip3 install tk
pip3 install matplotlib
pip3 install pyserial


