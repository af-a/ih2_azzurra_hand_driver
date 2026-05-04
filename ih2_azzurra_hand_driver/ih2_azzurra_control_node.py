#!/usr/bin/env python3

"""
Provides an interface for controlling the Prensilia IH2 Azzurra hand.
"""

import os
import time
import yaml

import rclpy

from rclpy.node import Node
from rclpy.action import ActionServer
from launch_ros.substitutions import FindPackageShare
from rcl_interfaces.msg import ParameterDescriptor, IntegerRange, SetParametersResult

from std_msgs.msg import Bool, String

from ih2_azzurra_hand_driver.ih2_hand_control import IH2AzzurraHandController, getHex
from ih2_azzurra_hand_driver_interfaces.msg import HandState
from ih2_azzurra_hand_driver_interfaces.action import MoveHand, MoveHandToNamedPose

# Colorized logging variables:
YELLOW = '\033[1;33m'
GREEN = '\033[92m'
RESET = '\033[0m'

## ----------------------------------------------------------------------
## ROS Nodes, Callbacks and Message Initializations:
## ----------------------------------------------------------------------

class Ih2AzzurraControlNode(Node):

    def __init__(self):
        super().__init__('ih2_azzurra_control_node')

        self.pkg_share_path = FindPackageShare(package='ih2_azzurra_hand_driver').find('ih2_azzurra_hand_driver')

        # Get node parameters:
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('pose_config_file_path', os.path.join(self.pkg_share_path, 'default_hand_poses.yaml'))
        self.declare_parameter('action_command_string', 'Type grasp name here...')

        self.serial_port = self.get_parameter('serial_port').value
        self.pose_config_file_path = self.get_parameter('pose_config_file_path').value
        self.action_command_topic = '~/action_command'
        self.hand_state_topic = '~/hand_state'

        # Initialize subscribers:
        self.action_command_subscription = self.create_subscription(String,
                                                                   self.action_command_topic,
                                                                   self.action_command_callback,
                                                                   10)
        # Initialize publishers:
        self.hand_state_publisher = self.create_publisher(HandState, self.hand_state_topic, 10)

        # Initialize action servers:
        self.move_hand_server = ActionServer(self, MoveHand, '~/MoveHand',
                                             self.move_hand_callback)
        self.move_hand_to_named_pose_server = ActionServer(self, MoveHandToNamedPose, '~/MoveHandToNamedPose', 
                                                           self.move_hand_to_named_pose_callback)

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
        self.hand_state_timer = self.create_timer(1 / publish_rate, self.hand_state_timer_callback)
        self.hand_state_msg = HandState()
        self.hand_state_msg.motor_name = list(self.hand_controller.doa_ids_dict.keys())

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

        self.executing_pose_motion = False

    def parameters_callback(self, params):
        modified_param_names = [param.name for param in params]
        modified_joint_param_names = list(set(modified_param_names).intersection(set(self.doa_names)))
        # self.get_logger().info(f'[DEBUG] modified_joint_param_names: {modified_joint_param_names}')

        if 'action_command_string' in modified_param_names:
            action_command_param = next(param for param in params if param.name == 'action_command_string')

            self.get_logger().info(f'Attempting to execute named pose "{action_command_param.value}"...')
            try:
                joint_positions_list = self.hand_poses_dict[action_command_param.value]
                self.execute_hand_pose(joint_positions_list)
                self.hand_state_msg.named_pose = action_command_param.value
            except KeyError:
                self.get_logger().warn(f'{YELLOW}Pose definition not found in pose config file! Ignoring request.{RESET}')

            return SetParametersResult(successful=True)
        elif modified_joint_param_names != []:
            desired_joint_states_list = [int(value) for value in self.hand_controller.get_pose()]
            for param in params:
                # self.get_logger().info(f'[DEBUG] Param modified: {param.name} --> {param.value}')
                if param.name in self.doa_names:
                    desired_joint_states_list[self.doa_names.index(param.name)] = int(param.value)

            if not self.executing_pose_motion:
                self.hand_controller.set_pose(joint_positions_list=desired_joint_states_list)
                self.hand_state_msg.named_pose = ''

            return SetParametersResult(successful=True)

    def hand_state_timer_callback(self):
        self.hand_state_msg.header.stamp = self.get_clock().now().to_msg()
        self.hand_state_msg.motor_position = self.hand_controller.get_pose()
        self.hand_state_msg.motor_moving = [bool(int(status_bits[-1])) for status_bits in self.hand_controller.get_finger_status()]
        self.hand_state_msg.motor_current = self.hand_controller.get_motor_currents()

        self.hand_state_publisher.publish(self.hand_state_msg)

    def action_command_callback(self, msg):
        self.get_logger().info(f'Attempting to execute named pose "{msg.data}"...')
        try:
            joint_positions_list = self.hand_poses_dict[msg.data]
            self.execute_hand_pose(joint_positions_list)
            self.hand_state_msg.named_pose = msg.data
        except KeyError:
            self.get_logger().warn(f'{YELLOW}Pose definition not found in pose config file! Ignoring request.{RESET}')

    def move_hand_callback(self, goal_handle):
        self.get_logger().info('Executing MoveHand goal...')
        desired_joint_states_list = [int(value) for value in goal_handle.request.desired_motor_position]
        self.execute_hand_pose(desired_joint_states_list)
        goal_handle.succeed()

        return MoveHand.Result(final_state=self.hand_state_msg)

    def move_hand_to_named_pose_callback(self, goal_handle):
        self.get_logger().info('Executing MoveHandToNamedPose goal...')

        desired_named_pose = goal_handle.request.desired_named_pose
        self.get_logger().info(f'Attempting to execute named pose "{desired_named_pose}"...')
        try:
            joint_positions_list = self.hand_poses_dict[desired_named_pose]
            self.execute_hand_pose(joint_positions_list)
            self.hand_state_msg.named_pose = desired_named_pose
            goal_handle.succeed()
            result = MoveHandToNamedPose.Result(final_state=self.hand_state_msg, success=True)
        except KeyError:
            self.get_logger().warn(f'{YELLOW}Pose definition not found in pose config file! Ignoring request.{RESET}')
            goal_handle.abort()
            result = MoveHandToNamedPose.Result(final_state=self.hand_state_msg, success=False)

        return result

    def execute_hand_pose(self, desired_joint_states_list):
        joint_positions_list = desired_joint_states_list
        self.hand_controller.set_pose(joint_positions_list=joint_positions_list)
        self.executing_pose_motion = True
        self.get_logger().info(f'{GREEN}Setting motor positions to {desired_joint_states_list}...{RESET}')

        # Update params:
        self.get_logger().info(f'Updating ROS parameters...')
        self.set_parameters([rclpy.parameter.Parameter(doa_name, rclpy.Parameter.Type.INTEGER, joint_positions_list[doa_id]) \
                                    for doa_id, doa_name in enumerate(self.doa_names)])
        self.executing_pose_motion = False


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
