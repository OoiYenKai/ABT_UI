#!/usr/bin/env python3
import os
import can


byte2 = 0.0
byte3 = 0.0
speed = 0.0
battery = 0.0


os.system('scripts/./can_setup.sh')

can_interface = 'can0'
bus = can.interface.Bus(channel=can_interface, bustype='socketcan') #socketcan native

initialize_msg = can.Message(arbitration_id=0x123, data=[0xa0, 0xb1, 0xc2, 0xd3, 0xe4, 0xf5, 0xf6, 0xff], is_extended_id=False)


try:
    #sending an initialization message
    bus.send(initialize_msg)
    print("Message sent on {}".format(can_interface))
except can.CanError:
    print('message was not sent')


def decoding_speed():
    try:
        while True:
            msg = bus.recv(0.5)
            if msg is None:
                break
            if msg.arbitration_id == 0x10FEF1C8:
                byte2 = hex(msg.data[1])
                byte3 = hex(msg.data[2])
                byte2 = byte2.replace("0x", "")
                #using little endian format
                xSpeed = byte3 + byte2 #speed in hexadecimal
                dSpeed = int(xSpeed, 16) #speed in decimal
                speed = dSpeed/256 #speed in km/h
                #print(speed)
                return "{:.2f}".format(speed)       
    except KeyboardInterrupt:
        bus.shutdown()
        os.system('sudo ifconfig can0 down')
        print('\n\rKeyboard interrupt received. Exiting.')
        exit()

def decoding_battery():
    try:
        while True:
            msg = bus.recv(0.5)
            if msg is None:
                break
            if msg.arbitration_id == 0x10FEFCC8:
                byte2 = hex(msg.data[1])
                dbattery = int(byte2, 16) #speed in decimal
                battery = dbattery * 0.4 #battery level in %
                #print(battery)
                return "{:.2f}".format(battery)       
    except KeyboardInterrupt:
        bus.shutdown()
        os.system('sudo ifconfig can0 down')
        print('\n\rKeyboard interrupt received. Exiting.')
        exit()