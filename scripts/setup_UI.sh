#! /usr/bin/bash

# Change to the right directory
cd ..

# Determine the Python version and install the corresponding venv package 
PYTHON_VERSION=$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1,2)
sudo apt install "python${PYTHON_VERSION}-venv"

# Create a virtual environment
python3 -m venv myenv

# Activate the virtual environment
source myenv/bin/activate

# install the required packages
sudo apt install net-tools
pip3 install textual
pip3 install textual-dev
pip3 install python-can
pip3 install pygame

# Get the directory where this script resides
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

SCRIPTS=(
    "$BASE_DIR/scripts/can_setup.sh"
    "$BASE_DIR/scripts/run_ABT_UI.sh"
    "$BASE_DIR/scripts/setup_UI.sh"
    "$BASE_DIR/ABT_UI.py"
    "$BASE_DIR/decoding.py"
)

# Make each script executable
for script in "${SCRIPTS[@]}"; do
    chmod +x "$script"
done

echo "Scripts have been made executable."

# Create a symbolic link to allow script to be run from anywhere
sudo ln -s $BASE_DIR/decoding.py /usr/local/bin/decoding
sudo ln -s $BASE_DIR/scripts/run_ABT_UI.sh /usr/local/bin/ABT_UI