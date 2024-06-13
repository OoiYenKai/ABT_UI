#!/usr/bin/env python3
import os
import can
import logging


class CANInterface:
    def __init__(self, interface='can0'):
        self.interface = interface
        self.bus = None

    def setup(self):
        os.system('scripts/./can_setup.sh')
        self.bus = can.interface.Bus(channel=self.interface, bustype='socketcan')

    def send_initial_message(self):
        initialize_msg = can.Message(arbitration_id=0x123, data=[0xa0, 0xb1, 0xc2, 0xd3, 0xe4, 0xf5, 0xf6, 0xff], is_extended_id=False)
        try:
            self.bus.send(initialize_msg)
            print(f"Message sent on {self.interface}")
        except can.CanError:
            print('Message was not sent')

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

    def shutdown(self):
        self.bus.shutdown()
        os.system(f'sudo ifconfig {self.interface} down')
        logging.info(f'CAN interface {self.interface} shutdown completed.')


def decoding_speed(msg):
    byte2 = hex(msg.data[1]).replace("0x", "")
    byte3 = hex(msg.data[2]).replace("0x", "")
    xSpeed = byte3 + byte2  # speed in hexadecimal
    dSpeed = int(xSpeed, 16)  # speed in decimal
    speed = dSpeed / 256  # speed in km/h
    return "{:.2f}".format(speed)


def decoding_battery(msg):
    byte2 = hex(msg.data[1]).replace("0x", "")
    dbattery = int(byte2, 16)  # battery level in decimal
    battery = dbattery * 0.4  # battery level in %
    return "{:.2f}".format(battery)

def main():
    can_interface = CANInterface()
    can_interface.setup()

    can_interface.send_initial_message()

    speed_msg_id = 0x18FEF1C8
    battery_msg_id = 0x18FEFCC8

    while True:
        speed_msg = can_interface.receive_message(speed_msg_id)
        if speed_msg:
            print("Speed:", decoding_speed(speed_msg))

        battery_msg = can_interface.receive_message(battery_msg_id)
        if battery_msg:
            print("Battery Level:", decoding_battery(battery_msg))



if __name__ == "__main__":
    main()