#!/bin/bash

# Install GNU Radio
sudo apt install -y gnuradio

# Ensure pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found, installing..."
    sudo apt install -y python3-pip
else
    echo "pip3 is already installed."
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