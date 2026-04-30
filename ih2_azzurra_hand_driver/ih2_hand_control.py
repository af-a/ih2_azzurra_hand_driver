#!/usr/bin/env python3

"""
Controls Prensilia IH2 Azzurra Hand.
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

    def __init__(self, serial_port='/dev/ttyUSB0', verbose=False):
        self.name = self.__class__.__name__

        self.serial_port = serial_port

        self.serial_interface_object = None

        self.doa_ids_dict = {'thumb_abduction': '00', 
                             'thumb_flexion': '01',
                             'index_flexion': '02', 
                             'middle_flexion': '03', 
                             'ring_little_flexion': '04'}

        self.verbose = verbose

    def initialize(self):
        self.serial_interface_object = serial.Serial()
        self.serial_interface_object.baudrate = 115200
        self.serial_interface_object.port = self.serial_port
        try:
            self.serial_interface_object.open()
        except serial.serialutil.SerialException as e:
            print(f'[INFO] [{self.name}] Caught exception: {e}')
            print(f'[INFO] [{self.name}] Check that the device in accessible' + \
                  f' on port {self.serial_port}!')
            return False

        return True

    def reset_hand(self):
        ## FirstCalibration:
        # self.serial_interface_object.write(bytes.fromhex('42'))
        ## FastCalibration:
        self.serial_interface_object.write(bytes.fromhex('46'))

    def abduct_thumb(self):
        self.serial_interface_object.write(bytes.fromhex('4400' + getHex(255)))

    def adduct_thumb(self):
        self.serial_interface_object.write(bytes.fromhex('4400' + getHex(0)))

    def set_pose(self, joint_positions_list=[255, 110, 100, 100, 255]):
        if self.verbose:
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

    def get_motor_currents(self):
        motor_currents_list = []
        for doa, id_str in self.doa_ids_dict.items():
            self.serial_interface_object.write(bytes.fromhex('49' + id_str))
            byte_1 = format(int.from_bytes(self.serial_interface_object.read(), byteorder='big'), '08b')
            byte_2 = format(int.from_bytes(self.serial_interface_object.read(), byteorder='big'), '08b')
            current_10_bit_value = byte_1[-2:] + byte_2
            if doa == 'thumb_abduction':
                current_float_value = 0.81 * int(current_10_bit_value, 2)
            else:
                current_float_value = 1.1 * int(current_10_bit_value, 2)

            motor_currents_list.append(current_float_value)

        return motor_currents_list

    def get_finger_status(self):
        # Note: the final bit in each string indicates whether that joint is in motion (1) or stationary (0)
        finger_status_string_list = []
        for doa, id_str in self.doa_ids_dict.items():
            self.serial_interface_object.write(bytes.fromhex('4B' + id_str))
            finger_status_string_list.append(format(int.from_bytes(self.serial_interface_object.read(), byteorder='big'), '08b'))
        return finger_status_string_list
