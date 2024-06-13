#!/usr/bin/env python3
from textual.app import App, ComposeResult
from textual.containers import Vertical, Center, Middle, Container
from textual.events import Resize
from textual.widgets import LoadingIndicator, TabbedContent, Label, Markdown, TabPane, ProgressBar, Static, Digits
from textual.geometry import Size
from textual import work
from decoding import CANInterface, decoding_speed, decoding_battery


SPEEDOMETER = """
# Speed:
"""

BATTERY = """
# Battery:
"""

OTHERS = """
# This is a tab for future expansion.
"""


class SpeedometerDigits(Static):
    def compose(self) -> ComposeResult:
        yield Digits(id="speedometerSpeed")

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return super().get_content_width(container, viewport)

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return super().get_content_height(container, viewport, width)


class BatteryDigits(Static):
    def compose(self) -> ComposeResult:
        yield Digits(id="batteryLevel")

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return super().get_content_width(container, viewport)

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return super().get_content_height(container, viewport, width)


class SpeedometerApp(App):
    BINDINGS = [
        ("T", "toggle_dark_mode", "Toggle dark mode")
    ]

    CSS_PATH = "ABT_UI.tcss"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.can_interface = CANInterface()
        self.can_interface.setup()

    def compose(self) -> ComposeResult:
        """The widgets that this app is composed of"""
        with TabbedContent(initial="vehicleData"):
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
        self.DecodingStatus = self.set_interval(0.1, self.get_vehicle_data, pause=False)

    @work(exclusive=True, thread=True, group="threaded_worker")
    async def get_vehicle_data(self) -> None:
        # get speed values
        speed_msg_id = 0x18FEF1C8
        battery_msg_id = 0x18FEFCC8

        speed_msg = self.can_interface.receive_message(speed_msg_id, timeout=0.5)
        if speed_msg:
            speed = decoding_speed(speed_msg)
            self.call_from_thread(self.update_speed_ui, float(speed))

        battery_msg = self.can_interface.receive_message(battery_msg_id, timeout=0.5)
        if battery_msg:
            battery = decoding_battery(battery_msg)
            self.call_from_thread(self.update_battery_ui, float(battery))

    def update_speed_ui(self, speed):
        speed_widget = self.query_one("#speedometerSpeed")
        speed_widget.update(str(speed))

    def update_battery_ui(self, battery):
        battery_widget = self.query_one("#batteryLevel")
        batteryBar = self.query_one("#batteryBar")
        battery_widget.update(str(battery))
        batteryBar.update(progress=battery)

    def on_resize(self, event: Resize) -> None:
        self.query_one("Screen").set_class(self.size.width < 85, "narrow")
        self.query_one("Screen").set_class(self.size.height < 22, "short")

    def action_toggle_dark_mode(self):
        """Toggle dark mode"""
        self.dark = not self.dark

    def quit_app(self):
        """Method to quit the UI application"""
        self.workers.cancel_group(self, "threaded_worker")
        self.DecodingStatus.pause()
        self.can_interface.shutdown()
        self.exit()


if __name__ == "__main__":
    try:
        app = SpeedometerApp()
        app.run()
    except KeyboardInterrupt:
        app.quit_app()