#!/usr/bin/env python3

"""
Provides an interface for controlling the Prensilia IH2 Azzurra hand.
"""

import time
import yaml

import rclpy

from rclpy.node import Node
from launch_ros.substitutions import FindPackageShare
from rcl_interfaces.msg import ParameterDescriptor, IntegerRange, SetParametersResult

from std_msgs.msg import Bool, String
from sensor_msgs.msg import JointState

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
        self.declare_parameter('action_command_topic', '~/action_command')
        self.declare_parameter('joint_states_topic', '~/joint_states')
        self.declare_parameter('pose_config_file_path', '/home/ahmed/workspace/ros2_ws/src/ih2_azzurra_hand_driver/config/default_hand_poses.yaml')
        self.declare_parameter('debug', False)

        self.serial_port = self.get_parameter('serial_port').value
        self.action_command_topic = self.get_parameter('action_command_topic').value
        self.joint_states_topic = self.get_parameter('joint_states_topic').value
        self.pose_config_file_path = self.get_parameter('pose_config_file_path').value
        self.debug = self.get_parameter('debug').value

        # Initialize subscribers:
        self.action_command_subscription = self.create_subscription(String,
                                                                   self.action_command_topic,
                                                                   self.action_command_callback,
                                                                   10)
        # Initialize publishers:
        self.joint_states_publisher = self.create_publisher(JointState, self.joint_states_topic, 10)

        # Initialize data variables:
        self.hand_controller = IH2AzzurraHandController(serial_port=self.serial_port)
        self.initialize()

    def initialize(self):
        if not self.hand_controller.initialize():
            self.get_logger().error(f'Could not initialize hand controller!')
            self.get_logger().error(f'Check that the device is accessible on serial_port {self.serial_port}.')
            self.get_logger().error(f'Shutting down...')
            raise SystemExit
            
        # Set up joint states publisher:
        publish_rate = 100
        self.joint_states_timer = self.create_timer(1 / publish_rate, self.joint_states_timer_callback)
        self.joint_states_msg = JointState()
        self.joint_states_msg.name = list(self.hand_controller.doa_ids_dict.keys())

        # Load default hand poses config:
        with open(self.pose_config_file_path, 'r') as file_handle:
            self.hand_poses_dict = yaml.safe_load(file_handle)

        # Initialize individual DoA control params:
        self.doa_names = list(self.hand_controller.doa_ids_dict.keys())
        initial_joint_positions = [int(value) for value in self.hand_controller.get_pose()]
        for doa_id, doa_name in enumerate(self.doa_names):
            self.declare_parameter(doa_name, 
                                   value=initial_joint_positions[doa_id],
                                   descriptor=ParameterDescriptor(name=doa_name,
                                                                  type=rclpy.Parameter.Type.INTEGER.value,
                                                                  integer_range=[IntegerRange(from_value=0, to_value=255, step=1)],
                                                                 ),
                                  )
        self.add_on_set_parameters_callback(self.parameters_callback)

    def parameters_callback(self, params):
        current_joint_states = [int(value) for value in self.hand_controller.get_pose()]
        for param in params:
            if param.name in self.doa_names:
                current_joint_states[self.doa_names.index(param.name)] = int(param.value)

        self.hand_controller.set_pose(joint_positions_list=current_joint_states)

        return SetParametersResult(successful=True)

    def joint_states_timer_callback(self):
        ## TODO: Create custom msg to allow ints or switch to saving deg values
        self.joint_states_msg.position = [float(value) for value in self.hand_controller.get_pose()]
        self.joint_states_publisher.publish(self.joint_states_msg)

    def action_command_callback(self, msg):
        self.get_logger().info(f'Received action command message: {msg.data}')
        self.get_logger().info(f'Attempting to execute pose...')
        try:
            self.hand_controller.set_pose(joint_positions_list=self.hand_poses_dict[msg.data])
        except KeyError:
            self.get_logger().warn(f'Pose definition not found in pose config file! Ignoring request.')

def main(args=None):
    ## ----------------------------------------------------------------------
    ## ROS Initializations:
    ## ----------------------------------------------------------------------
    rclpy.init(args=args)
    ih2_azzurra_control_node = Ih2AzzurraControlNode()

    ## ----------------------------------------------------------------------
    ## Execution:
    ## ----------------------------------------------------------------------

    ih2_azzurra_control_node.get_logger().info(f'Will listen to messages for action command ' + \
                                               f'({ih2_azzurra_control_node.action_command_topic}) ' + \
                                               f'...')
    try:
        rclpy.spin(ih2_azzurra_control_node)
    except SystemExit:
        rclpy.logging.get_logger('rclpy').info('Stopping node...')

    ih2_azzurra_control_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
