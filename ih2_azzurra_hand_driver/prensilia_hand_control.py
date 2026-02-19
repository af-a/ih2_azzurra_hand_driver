#!/usr/bin/env python3

"""
Controls Prensilia Hand.
"""

import os
import time
import argparse

# Note: from pyserial module:
import serial


## ----------------------------------------------------------------------
## Helper functions:
## ----------------------------------------------------------------------

def getHex(dataint):
    """
    Converts integer to hex value.

    Based on code from ControlPresnilia_linux.py script.

    Note from original documentation:
    "Prensillia using 8 bit (0~255) to send and position the finger"

    Parameters
    ----------
    dataint: int
        Input integer value

    Returns
    -------
    dataHex: str
        Output hexadecimal value (as a string)
    """
    dataHex = str()
    if dataint < 16:
        dataHex = "0" + format(dataint, 'x')
    else: 
        dataHex = format(dataint, 'x')
    return dataHex


class PrensiliaHandController(object):
    """
    Interfaces with and exposes some functionalities of the Prensilia
    hand.
    """

    def __init__(self, serial_port='/dev/ttyUSB0', debug=False):
        self.name = self.__class__.__name__

        self.serial_port = serial_port

        self.serial_interface_object = None

    def initialize(self):
        self.serial_interface_object = serial.Serial()
        self.serial_interface_object.baudrate = 115200
        self.serial_interface_object.port = self.serial_port
        self.serial_interface_object.open()

    def reset_hand(self):
        ## FirstCalibration:
        # self.serial_interface_object.write(bytes.fromhex('42'))
        ## FastCalibration:
        self.serial_interface_object.write(bytes.fromhex('46'))

    def open_all(self):
        ## Note: for some reason, does not affect joint 00 (thumb):
        self.serial_interface_object.write(bytes.fromhex('48' + getHex(0) + getHex(0) + getHex(0) + getHex(0) + getHex(0) + '48'))

    def abduct_thumb(self):
        self.serial_interface_object.write(bytes.fromhex('4400' + getHex(255)))

    def adduct_thumb(self):
        self.serial_interface_object.write(bytes.fromhex('4400' + getHex(0)))

    ## Unused:
    def get_motor_currents(self):
        self.serial_interface_object.write(bytes.fromhex('4400' + getHex(255)))

    def execute_sequence(self, sequence_id):
        print(f'[INFO] [{self.name}] Executing sequence {sequence_id}...')
        if sequence_id == 0:
            print(f'[INFO] [{self.name}] Opening all fingers...')
            # self.open_all()
            self.serial_interface_object.write(bytes.fromhex('48' + getHex(0) + getHex(0) + getHex(0) + getHex(0) + getHex(0) + '48'))
        elif sequence_id == 1:
            print(f'[INFO] [{self.name}] Closing three fingers simultaneously...')
            for finger_hex_string in ['02', '03', '04']:
                self.serial_interface_object.write(bytes.fromhex('44' + finger_hex_string + getHex(255)))
        elif sequence_id == 2:
            print(f'[INFO] [{self.name}] Going to closing posture {sequence_id}...')
            self.serial_interface_object.write(bytes.fromhex('48' + getHex(255) + getHex(130) + getHex(130) + getHex(130) + getHex(130) + '48'))
        else:
            print(f'[WARN] [{self.name}] Invalid sequence ID! Skipping execution')

    def go_to_pose(self, joint_positions_list=[255, 110, 100, 100, 255]):
        self.serial_interface_object.write(bytes.fromhex('48' + getHex(joint_positions_list[0]) + getHex(joint_positions_list[1]) + \
                                                         getHex(joint_positions_list[2]) + getHex(joint_positions_list[3]) + \
                                                         getHex(joint_positions_list[4]) + '48'))
