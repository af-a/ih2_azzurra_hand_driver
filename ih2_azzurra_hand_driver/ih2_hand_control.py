#!/usr/bin/env python3

"""
Controls PrensiliaIH2 Azzurra Hand.
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

    Based on code from ControlPrensilia_linux.py script.

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


class IH2AzzurraHandController(object):
    """
    Interfaces with and exposes some functionalities of the IH2 Azzurra
    hand.
    """

    def __init__(self, serial_port='/dev/ttyUSB0', debug=False):
        self.name = self.__class__.__name__

        self.serial_port = serial_port

        self.serial_interface_object = None


        self.doa_ids_dict = {'thumb_abduction': '00', 
                             'thumb_flexion': '01',
                             'index_flexion': '02', 
                             'middle_flexion': '03', 
                             'ring_little_flexion': '04'}

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

    def open_hand(self):
        ## Note: for some reason, does not affect joint 00 (thumb):
        self.serial_interface_object.write(bytes.fromhex('48' + getHex(0) + getHex(0) + getHex(0) + getHex(0) + getHex(0) + '48'))

    def abduct_thumb(self):
        self.serial_interface_object.write(bytes.fromhex('4400' + getHex(255)))

    def adduct_thumb(self):
        self.serial_interface_object.write(bytes.fromhex('4400' + getHex(0)))

    ## Unused:
    def get_motor_currents(self):
        self.serial_interface_object.write(bytes.fromhex('4400' + getHex(255)))

    def set_pose(self, joint_positions_list=[255, 110, 100, 100, 255]):
        print(f'[INFO] [{self.name}] Going to pose: {joint_positions_list}...')
        self.serial_interface_object.write(bytes.fromhex('48' + getHex(joint_positions_list[0]) + getHex(joint_positions_list[1]) + \
                                                         getHex(joint_positions_list[2]) + getHex(joint_positions_list[3]) + \
                                                         getHex(joint_positions_list[4]) + '48'))

    def get_pose(self):
        joint_positions_list = []
        for doa, id_str in self.doa_ids_dict.items():
            self.serial_interface_object.write(bytes.fromhex('45' + id_str))
            joint_positions_list.append(int.from_bytes(self.serial_interface_object.read(), byteorder='big'))

        return joint_positions_list
