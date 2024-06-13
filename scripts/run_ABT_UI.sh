#! /usr/bin/bash

# Change to the directory where the python script is located
cd '/home/yenkai/Documents/CAG_Project'

# source the virtual environment
source myenv/bin/activate

# Run the app
textual run --dev ABT_UI.py

# When the app is not running anymore, bring down the CAN interface
sudo ifconfig can0 down