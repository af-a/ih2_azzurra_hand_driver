#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument 
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    serial_port_launch_arg = DeclareLaunchArgument(
        'serial_port', 
        default_value='/dev/ttyUSB0',
        description='TODO'
    )
    action_command_topic_launch_arg = DeclareLaunchArgument(
        'action_command_topic', 
        default_value='~/action_command',
        description='TODO'
    )
    joint_states_topic_launch_arg = DeclareLaunchArgument(
        'joint_states_topic', 
        default_value='~/joint_states',
        description='TODO'
    )
    debug_launch_arg = DeclareLaunchArgument(
        'debug', 
        default_value='False',
        description='TODO'
    )

    prensilia_control_node_name = 'new_driver_node'
    prensilia_control_node = Node(
        package='ih2_azzurra_hand_driver',
        executable='new_driver_node',
        name=prensilia_control_node_name,
        parameters=[
            {'serial_port': LaunchConfiguration('serial_port')},
            {'action_command_topic': LaunchConfiguration('action_command_topic')},
            {'debug': LaunchConfiguration('debug')},
        ],
    )

    rqt_reconfigure_node = Node(
        package='rqt_reconfigure',
        executable='rqt_reconfigure',
        name='ih2_rqt_reconfigure',
        arguments=[f'/{prensilia_control_node_name}']
    )

    return LaunchDescription([
        serial_port_launch_arg,
        action_command_topic_launch_arg,
        joint_states_topic_launch_arg,
        debug_launch_arg,
        prensilia_control_node, 
        rqt_reconfigure_node,
    ])
