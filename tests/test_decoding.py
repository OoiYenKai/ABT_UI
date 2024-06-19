import sys
import os
# Add the project directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import decoding
import pytest
import can

class MockCANBus:
    def __init__(self):
        self.sent_messages = []

    def send(self, msg):
        self.sent_messages.append(msg)

    def recv(self, timeout=None):
        if self.sent_messages:
            return self.sent_messages.pop(0)
        return None

@pytest.fixture
def can_interface():
    interface = decoding.CANInterface()
    interface.bus = MockCANBus()
    return interface

def test_decoding_speed():
    # Create a mock CAN message for speed
    msg = can.Message(arbitration_id=0x18FEF1C8, data=[0x00, 0xEA, 0x17, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=True)
    speed = decoding.decoding_speed(msg)
    assert speed == "23.91"  # (0x17EA in hex is 6122 in decimal, 6122/256 = 23.91)

def test_decoding_battery():
    # Create a mock CAN message for battery level
    msg = can.Message(arbitration_id=0x18FEFCC8, data=[0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=True)
    battery_level = decoding.decoding_battery(msg)
    assert battery_level == "40.00"  # (0x64 in hex is 100 in decimal, 100 * 0.4 = 40.0)

def test_send_initial_message(can_interface):
    can_interface.send_initial_message()
    sent_message = can_interface.bus.sent_messages[0]
    assert sent_message.arbitration_id == 0x123
    assert sent_message.data == bytearray([0xa0, 0xb1, 0xc2, 0xd3, 0xe4, 0xf5, 0xf6, 0xff])

def test_receive_message(can_interface):
    msg = can.Message(arbitration_id=0x18FEF1C8, data=[0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=True)
    can_interface.bus.sent_messages.append(msg)
    received_msg = can_interface.receive_message(0x18FEF1C8)
    assert received_msg.arbitration_id == 0x18FEF1C8
    assert received_msg.data == bytearray([0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00])

if __name__ == "__main__":
    pytest.main()