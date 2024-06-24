# Automatic Baggage Tractor UI

This Python application is designed to interface with a Vehicle Area Network (CAN bus) to retrieve and display real-time vehicle data, specifically speed and battery level. It utilizes the Textual library for creating a terminal-based user interface (UI) and Pygame for audio alerts.

## Features

- **Real-time Data Display:** Displays vehicle speed (km/h) and battery level (%).
- **Alert System:** Plays an alert sound when the vehicle speed exceeds a threshold or when the battery level drops below a certain threshold.
- **User Interface:** Utilizes a terminal-based UI with tabbed views for displaying different tabs
- **Dark Mode:** Supports toggling dark mode using the 'T' key.
- **Responsive display:** Changes the layout of the UI to adaptto different screen sizes of different devices.

## Dependencies

- **Python Libraries:**
  - Textual: For building the terminal UI.
  - Pygame: For playing audio alerts.
  - CAN (python-can): For interfacing with the CAN bus.
  - Pytest: For unit testing
  
  
## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/OoiYenKai/ABT_UI.git
   cd ABT_UI
   ```
2. Create virtual environment and install dependencies:

    ```bash
    cd scripts
    ./setup_UI.sh
    ```

## Usage

**Set up the can interface:** You will need to run some commands in order to get the CAN controller up and running, follow the instructions on this link: https://www.waveshare.com/wiki/2-CH_CAN_HAT.

**Run the application:**

   ```bash
    ABT_UI
  ```

**Interface with the CAN bus:** Ensure the CAN bus is set up and running on the can0 interface. The application will display real-time speed and battery level data in the terminal UI.

**Toggle dark mode:**
Press 'T' to toggle between light and dark modes.

**Exit the application:**
Press Ctrl + C to quit the application and shut down the CAN interface gracefully.

## Contributing

Contributions are welcomed! If you have suggestions or improvements, please fork the repository, create a new branch, and submit a pull request.
