#!/usr/bin/env python3

"""
Provides an interface for controlling the Prensilia IH2 Azzurra hand.
"""

import time

import rclpy

from rclpy.node import Node
from launch_ros.substitutions import FindPackageShare

from std_msgs.msg import Bool, String

from ih2_azzurra_hand_driver.ih2_hand_control import IH2AzzurraHandController, getHex

## ----------------------------------------------------------------------
## ROS Nodes, Callbacks and Message Initializations:
## ----------------------------------------------------------------------

class Ih2AzzurraControlNode(Node):

    def __init__(self):
        super().__init__('ih2_azzurra_control_node')

        self.pkg_share_path = FindPackageShare(package='ih2_azzurra_hand_driver').find('ih2_azzurra_hand_driver')

        # Get node parameters:
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('open_trigger_topic', '~/open_trigger')
        self.declare_parameter('grasp_trigger_topic', '~/grasp_trigger')
        self.declare_parameter('action_command_topic', '~/action_command')
        self.declare_parameter('pose_config_file_path', '/home/ahmed/workspace/ros2_ws/src/ih2_azzurra_hand_driver/config/default_hand_poses.yaml')
        self.declare_parameter('debug', False)

        self.serial_port = self.get_parameter('serial_port').value
        self.open_trigger_topic = self.get_parameter('open_trigger_topic').value
        self.grasp_trigger_topic = self.get_parameter('grasp_trigger_topic').value
        self.action_command_topic = self.get_parameter('action_command_topic').value
        self.pose_config_file_path = self.get_parameter('pose_config_file_path').value
        self.debug = self.get_parameter('debug').value

        # Initialize subscribers:
        self.open_trigger_subscription = self.create_subscription(Bool,
                                                                  self.open_trigger_topic,
                                                                  self.open_trigger_callback,
                                                                  10)
        self.grasp_trigger_subscription = self.create_subscription(Bool,
                                                                   self.grasp_trigger_topic,
                                                                   self.grasp_trigger_callback,
                                                                   10)
        self.action_command_subscription = self.create_subscription(String,
                                                                   self.action_command_topic,
                                                                   self.action_command_callback,
                                                                   10)

        self.hand_controller = IH2AzzurraHandController(serial_port=self.serial_port)
        
        # Initialize data variables:
        self.initialize()

    def initialize(self):
        self.hand_controller.initialize()

        self.last_message_time_stamp = None

    def open_trigger_callback(self, msg):
        self.get_logger().info('Received open trigger message. Opening gripper...')
        # TODO: Add wait mechanism
        self.hand_controller.execute_sequence(0)

    def grasp_trigger_callback(self, msg):
        self.get_logger().info('Received grasp trigger message. Grasping...')
        # TODO: Add wait mechanism
        self.hand_controller.execute_sequence(2)

    def action_command_callback(self, msg):
        self.get_logger().info(f'Received action command message: {msg.data}')
        # TODO: Add wait mechanism
        if msg.data == 'tri_pre_grasp':
            self.get_logger().info(f'Executing Tri-pregrasp...')
            self.hand_controller.go_to_pose(joint_positions_list=[255, 110, 100, 100, 255])
        elif msg.data == 'tri_grasp':
            self.get_logger().info(f'Executing Tri-grasp...')
            self.hand_controller.go_to_pose(joint_positions_list=[255, 120, 170, 180, 255])
        elif msg.data == 'tri_pre_grasp_objects':
            self.get_logger().info(f'Executing Tri-pregrasp for objects...')
            self.hand_controller.go_to_pose(joint_positions_list=[255, 40, 60, 60, 255])
        elif msg.data == 'tri_grasp_objects':
            self.get_logger().info(f'Executing Tri-grasp for objects...')
            self.hand_controller.go_to_pose(joint_positions_list=[255, 160, 100, 100, 255])
        # elif msg.data == 'gradual_open_tri_grasp_objects':
        #     self.get_logger().info(f'Executing gradual open for Tri-grasp for objects...')
            # self.hand_controller.execute_objects_tri_grasp_gradual_open()
        elif msg.data == 'open':
            self.get_logger().info(f'Executing full open...')
            self.hand_controller.open_all()
        else:
            self.get_logger().info(f'[WARN] Invalid action command! Ignoring request.')

def main(args=None):
    ## ----------------------------------------------------------------------
    ## ROS Initializations:
    ## ----------------------------------------------------------------------
    rclpy.init(args=args)
    ih2_azzurra_control_node = Ih2AzzurraControlNode()

    ## ----------------------------------------------------------------------
    ## Execution:
    ## ----------------------------------------------------------------------

    ih2_azzurra_control_node.get_logger().info(f'Will listen to messages for opening hand ' + \
                                               f'({ih2_azzurra_control_node.open_trigger_topic}) ' + \
                                               f'or grasping ({ih2_azzurra_control_node.grasp_trigger_topic})' + \
                                               f'...')
    try:
        rclpy.spin(ih2_azzurra_control_node)
    except SystemExit:
        rclpy.logging.get_logger('rclpy').info('Stopping node...')

    ih2_azzurra_control_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
