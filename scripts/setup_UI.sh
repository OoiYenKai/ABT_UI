#! /usr/bin/bash

# Change to the right directory
cd '/home/yenkai/Documents/CAG_Project'

#download the venv package
sudo apt install python3.11-venv

# Create a virtual environment
python3 -m venv myenv

# Activate the virtual environment
source myenv/bin/activate

# install the required packages
sudo apt install net-tools
pip3 install textual
pip3 install textual-dev
pip3 install python-can

# Make the scripts executable
chmod +x '/home/yenkai/Documents/CAG_Project/scripts/can_setup.sh'
chmod +x '/home/yenkai/Documents/CAG_Project/scripts/run_ABT_UI.sh'
chmod +x '/home/yenkai/Documents/CAG_Project/scripts/setup_UI.sh'
chmod +x '/home/yenkai/Documents/CAG_Project/ABT_UI.py'
chmod +x '/home/yenkai/Documents/CAG_Project/decoding.py'

# Create a symbolic link to allow script to be run from anywhere
sudo ln -s /home/yenkai/Documents/CAG_Project/decoding.py /usr/local/bin/decoding
sudo ln -s /home/yenkai/Documents/CAG_Project/scripts/run_ABT_UI.sh /usr/local/bin/ABT_UI