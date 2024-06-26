#!/usr/bin/env python3

# Import necessary modules
from textual.app import App, ComposeResult
from textual.containers import Vertical, Center, Middle, Container
from textual.events import Resize
from textual.widgets import LoadingIndicator, TabbedContent, Label, Markdown, TabPane, ProgressBar, Static, Digits
from textual.geometry import Size
from textual import work
import pygame
import threading

# Import CAN interface and decoding functions from decoding module
from decoding import CANInterface, decoding_speed, decoding_battery

# Initialize Pygame mixer
pygame.mixer.init()

# Thresholds for alert
SPEED_THRESHOLD = 40.0
BATTERY_THRESHOLD = 20.0
BATTERY_CRITICAL_THRESHOLD = 10.0

# Path to alert audio file
ALERT_SOUND_PATH = "audio/alert.wav"

SPEEDOMETER = """
# Speed:
"""

BATTERY = """
# Battery:
"""

OTHERS = """
# This is a tab for future expansion.
"""

# Static widget for displaying speedometer Digits
class SpeedometerDigits(Static):
    def compose(self) -> ComposeResult:
        yield Digits(id="speedometerSpeed")

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return super().get_content_width(container, viewport)

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return super().get_content_height(container, viewport, width)


# Static widget for displaying battery level Digits
class BatteryDigits(Static):
    def compose(self) -> ComposeResult:
        yield Digits(id="batteryLevel")

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return super().get_content_width(container, viewport)

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return super().get_content_height(container, viewport, width)


# Main application class inheriting from App
class ABTApp(App):
    # Key bindings for the application
    BINDINGS = [
        ("T", "toggle_dark_mode", "Toggle dark mode")
    ]

    # Path to CSS file for styling
    CSS_PATH = "ABT_UI.tcss"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize CAN interface for handling CAN bus operations
        self.can_interface = CANInterface()
        self.can_interface.setup()  # Setup CAN interface on initialization
        self.battery_alert_triggered = False  # Track if battery alert has been triggered
        self.battery_alert_active = True  # Track if battery alert is active
        self.battery_critical_alert_active = True  # Track if critical battery alert is active

    def compose(self) -> ComposeResult:
        """Compose method defining the layout of the application"""
        with TabbedContent(initial="vehicleData", id="UItabbedcontent"):
            with TabPane("Vehicle Data", id="vehicleData"):
                with Vertical():
                    with Middle(id="speed_middle"):
                        with Center(id="markdown_center1"):
                            yield Markdown(SPEEDOMETER, id="speedometerDisplay")
                        with Container(id="speedometer_container"):
                            with Center(id="speedometerSpeed_center"):
                                yield SpeedometerDigits()
                            with Center(id="label_center"):
                                yield Label("km/h", id="speedUnitLabel")
                with Vertical():
                    with Middle(id="battery_middle"):
                        with Center(id="markdown_center2"):
                            yield Markdown(BATTERY, id="batteryDisplay")
                        with Container(id="battery_container"):
                            with Center(id="batterylevel_center"):
                                yield BatteryDigits()
                            with Center(id="progress_center"):
                                yield ProgressBar(total=100, show_eta=False, id="batteryBar")
            with TabPane("Others", id="others"):
                with Vertical():
                    with Center():
                        yield Markdown(OTHERS, id="othersDisplay")
                    yield LoadingIndicator(id="loading")

    def on_mount(self) -> None:
        """
        Callback method called when the application mounts
        Starts an infinite timer with 100 msecs intervals
        """
        self.DecodingStatus = self.set_interval(0.1, self.get_vehicle_data, pause=False)

    # Coroutine to fetch vehicle data such as speed and battery level
    @work(exclusive=True, thread=True, group="threaded_worker")
    async def get_vehicle_data(self) -> None:
        """The specific CAN IDs to receive CAN messages from"""
        rpm_msg_id = 0x385
        battery_msg_id = 0x414

        # Receive and process speed data
        speed_msg = self.can_interface.receive_message(rpm_msg_id, timeout=0.5)
        if speed_msg:
            speed = decoding_speed(speed_msg)
            self.call_from_thread(self.update_speed_ui, float(speed))
            if float(speed) >= SPEED_THRESHOLD and not self.battery_alert_triggered:
                self.battery_alert_triggered = True
                self.play_alert_sound()

        # Receive and process battery level data
        battery_msg = self.can_interface.receive_message(battery_msg_id, timeout=0.5)
        if battery_msg:
            battery = decoding_battery(battery_msg)
            self.call_from_thread(self.update_battery_ui, float(battery))
            if float(battery) <= BATTERY_CRITICAL_THRESHOLD and self.battery_critical_alert_active:
                self.battery_critical_alert_active = False
                self.play_critical_alert_sound()
            elif float(battery) <= BATTERY_THRESHOLD and self.battery_alert_active and float(battery) > BATTERY_CRITICAL_THRESHOLD:
                self.battery_alert_active = False
                self.play_alert_sound()
            elif float(battery) > BATTERY_CRITICAL_THRESHOLD and not self.battery_critical_alert_active:
                self.battery_critical_alert_active = True
            elif float(battery) > BATTERY_THRESHOLD and not self.battery_alert_active:
                self.battery_alert_active = True

    def play_alert_sound(self):
        """Play battery alert sound for 3 seconds"""
        pygame.mixer.music.load(ALERT_SOUND_PATH)
        pygame.mixer.music.play()
        threading.Timer(2.0, self.stop_alert_sound).start()

    def play_critical_alert_sound(self):
        """Play critical battery alert sound 3 times at 1-second intervals"""
        self.critical_alert_count = 0
        self.play_critical_alert()

    def play_critical_alert(self):
        """Helper function to play critical alert sound"""
        if self.critical_alert_count < 3:
            pygame.mixer.music.load(ALERT_SOUND_PATH)
            pygame.mixer.music.play()
            self.critical_alert_count += 1
            threading.Timer(1.0, self.play_critical_alert).start()
        else:
            self.stop_critical_alert_sound()

    def stop_alert_sound(self):
        """Stop the alert sound"""
        pygame.mixer.music.stop()
        self.battery_alert_triggered = False

    def stop_critical_alert_sound(self):
        """Stop the critical alert sound"""
        pygame.mixer.music.stop()
        self.battery_alert_triggered = False

    def update_speed_ui(self, speed):
        """Update UI with the received speed data"""
        speed_widget = self.query_one("#speedometerSpeed")
        speed_widget.update(str(speed))

    def update_battery_ui(self, battery):
        """Update UI with the received battery level data"""
        battery_widget = self.query_one("#batteryLevel")
        batteryBar = self.query_one("#batteryBar")
        battery_widget.update(str(battery))
        batteryBar.update(progress=battery)

    def on_resize(self, event: Resize) -> None:
        """Callback method called when the terminal is resized"""
        self.query_one("Screen").set_class(self.size.width < 85, "narrow")
        self.query_one("Screen").set_class(self.size.height < 22, "short")

    def action_toggle_dark_mode(self):
        """Toggle dark mode"""
        self.dark = not self.dark

    def quit_app(self):
        """Method to cleanly quit the UI application"""
        self.workers.cancel_group(self, "threaded_worker")  # Cancel threaded worker group
        self.DecodingStatus.pause()  # Pause decoding status timer
        self.can_interface.shutdown()  # Shutdown CAN interface
        self.exit()  # Exit the application


if __name__ == "__main__":
    try:
        app = ABTApp()
        app.run()
    except KeyboardInterrupt:
        app.quit_app()