import pytest
import pygame
import time
import asyncio
import sys
import os
# Add the project directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ABT_UI  

@pytest.fixture
def app():
    app = ABT_UI.ABTApp()
    return app

def test_initialization(app):
    assert app.can_interface is not None
    assert app.can_interface.bus is not None

def test_toggle_dark_mode(app):
    initial_dark_mode = app.dark
    app.action_toggle_dark_mode()
    assert app.dark != initial_dark_mode

@pytest.mark.asyncio
async def test_on_resize_narrow_short():
    app = ABT_UI.ABTApp()
    async with app.run_test(size=(80, 20)) as pilot:
        # Simulate the resize event
        screen = app.query_one("Screen")
        assert screen.has_class("narrow")
        assert screen.has_class("short")

@pytest.mark.asyncio
async def test_on_resize_narrow():
    app = ABT_UI.ABTApp()
    async with app.run_test(size=(80, 24)) as pilot:
        # Simulate the resize event
        screen = app.query_one("Screen")
        assert screen.has_class("narrow")
        assert not screen.has_class("short")

@pytest.mark.asyncio
async def test_on_resize_short():
    app = ABT_UI.ABTApp()
    async with app.run_test(size=(85, 20)) as pilot:
        # Simulate the resize event
        screen = app.query_one("Screen")
        assert not screen.has_class("narrow")
        assert screen.has_class("short")

@pytest.mark.asyncio
async def test_on_resize_default():
    app = ABT_UI.ABTApp()
    async with app.run_test(size=(85, 24)) as pilot:
        # Simulate the resize event
        screen = app.query_one("Screen")
        assert not screen.has_class("narrow")
        assert not screen.has_class("short")



@pytest.mark.asyncio
async def test_update_speed_ui():
    app = ABT_UI.ABTApp()
    async with app.run_test() as pilot:
        # Simulate updating speed to 50
        app.update_speed_ui(50)
        
        # Verify that the speedometerSpeed widget was updated correctly
        speed_widget = app.query_one("#speedometerSpeed")
        assert speed_widget.value == "50", "Speedometer speed should be updated to 50"

@pytest.mark.asyncio
async def test_update_battery_ui():
    app = ABT_UI.ABTApp()
    async with app.run_test() as pilot:
        # Simulate updating battery level to 75
        app.update_battery_ui(75)
        
        # Verify that the batteryLevel widget was updated correctly
        battery_widget = app.query_one("#batteryLevel")
        assert battery_widget.value == "75", "Battery level should be updated to 75"

        # Verify that the batteryBar progress was updated correctly
        battery_bar = app.query_one("#batteryBar")
        assert battery_bar.progress == 75, "Battery progress bar should be updated to 75"

@pytest.mark.asyncio
async def test_play_and_stop_alert_sound(mocker):
    # Mock necessary dependencies (assuming pygame.mixer.music)
    mocker.patch.object(pygame.mixer, 'music')

    app = ABT_UI.ABTApp()

    # Mock the play and stop methods of pygame.mixer.music
    mocker.patch.object(pygame.mixer.music, 'load')
    mocker.patch.object(pygame.mixer.music, 'play')
    mocker.patch.object(pygame.mixer.music, 'stop')

    # Call play_alert_sound and wait a bit to simulate playing the sound
    app.play_alert_sound()
    await asyncio.sleep(1)  # Adjust time as needed

    # Verify that pygame.mixer.music.load and pygame.mixer.music.play were called
    pygame.mixer.music.load.assert_called_once_with("audio/alert.wav")
    pygame.mixer.music.play.assert_called_once()

    # Wait for the alert sound to play (time adjusted based on your application's logic)
    time.sleep(4)  # Adjust time based on the expected duration of the sound

    # After 4 seconds (adjust according to your timer duration), verify that stop was called
    pygame.mixer.music.stop.assert_called_once()

@pytest.mark.asyncio
async def test_switch_tabs_by_key_press():
    app = ABT_UI.ABTApp()
    async with app.run_test() as pilot:
        # Verify initial tab ("Vehicle Data") is active
        tabbed_content = app.query_one("#UItabbedcontent")
        vehicle_data_tab = app.query_one("#vehicleData")
        assert vehicle_data_tab.disabled == False, "Vehicle Data tab should be initially visible"
        assert tabbed_content.active == "vehicleData"

        # Simulate pressing a key to switch tabs (e.g., "TAB" key press)
        await pilot.press("right")

        # Verify that the new tab ("Others") is now active
        others_tab = app.query_one("#others")
        assert others_tab.disabled == False, "Others tab should be active after key press"
        assert tabbed_content.active == "others"