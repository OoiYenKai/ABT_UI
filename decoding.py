#!/usr/bin/env python3
import os
import can
import math


# Define CAN interface class for handling CAN bus operations
class CANInterface:
    def __init__(self, interface='can0'):
        self.interface = interface
        self.bus = None

    # Setup the CAN bus interface
    def setup(self):
        os.system('scripts/./can_setup.sh')
        self.bus = can.interface.Bus(channel=self.interface, bustype='socketcan')

    # Send a message through can0 channel
    def send_initial_message(self):
        initialize_msg = can.Message(arbitration_id=0x123, data=[0xa0, 0xb1, 0xc2, 0xd3, 0xe4, 0xf5, 0xf6, 0xff], is_extended_id=False)
        try:
            self.bus.send(initialize_msg)
            print(f"Message sent on {self.interface}")
        except can.CanError:
            print('Message was not sent')

    # Receive CAN messages with a specific ID
    def receive_message(self, arbitration_id, timeout=0.5):
        try:
            while True:
                msg = self.bus.recv(timeout)
                if msg is None:
                    return None
                if msg.arbitration_id == arbitration_id:
                    return msg
        except KeyboardInterrupt:
            self.shutdown()
            print('\n\rKeyboard interrupt received. Exiting.')
            exit()

    # Gracefully shutdown the CAN interface
    def shutdown(self):
        self.bus.shutdown()
        os.system(f'sudo ifconfig {self.interface} down')


# Function to decode speed from a CAN message
def decoding_speed(msg):
    byte5 = hex(msg.data[4]).replace("0x", "")
    byte6 = hex(msg.data[5]).replace("0x", "")
    xThrottle = byte6 + byte5  # Throttle(rpm) in hexadecimal
    dThrottle = int(xThrottle, 16)  # Throttle(rpm) in decimal
    speed = (math.pi * 0.7 * dThrottle * 60)/(24.2 * 1000) # Speed in Km/h
    return "{:.2f}".format(speed)

# Function to decode battery levels from a CAN message
def decoding_battery(msg):
    byte5 = hex(msg.data[4]).replace("0x", "")
    dbattery = int(byte5, 16)  # battery level in decimal
    battery = dbattery * 0.4  # battery level in %
    return "{:.2f}".format(battery)

def main():
    can_interface = CANInterface()
    can_interface.setup()

    can_interface.send_initial_message()

    # The specific CAN IDs to receive CAN messages from
    rpm_msg_id = 0x385
    battery_msg_id = 0x414

    while True:
        rpm_msg = can_interface.receive_message(rpm_msg_id)
        if rpm_msg:
            print("Speed:", decoding_speed(rpm_msg))

        battery_msg = can_interface.receive_message(battery_msg_id)
        if battery_msg:
            print("Battery Level:", decoding_battery(battery_msg))

if __name__ == "__main__":
    main()