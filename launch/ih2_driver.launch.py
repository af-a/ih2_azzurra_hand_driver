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
    open_trigger_topic_launch_arg = DeclareLaunchArgument(
        'open_trigger_topic', 
        default_value='~/open_trigger',
        description='TODO'
    )
    grasp_trigger_topic_launch_arg = DeclareLaunchArgument(
        'grasp_trigger_topic', 
        default_value='~/grasp_trigger',
        description='TODO'
    )
    action_command_topic_launch_arg = DeclareLaunchArgument(
        'action_command_topic', 
        default_value='~/action_command',
        description='TODO'
    )
    debug_launch_arg = DeclareLaunchArgument(
        'debug', 
        default_value='False',
        description='TODO'
    )

    prensilia_control_node = Node(
        package='ih2_azzurra_hand_driver',
        executable='new_driver_node',
        name='new_driver_node',
        parameters=[
            {'serial_port': LaunchConfiguration('serial_port')},
            {'open_trigger_topic': LaunchConfiguration('open_trigger_topic')},
            {'grasp_trigger_topic': LaunchConfiguration('grasp_trigger_topic')},
            {'action_command_topic': LaunchConfiguration('action_command_topic')},
            {'debug': LaunchConfiguration('debug')},
        ],
    )

    return LaunchDescription([
        serial_port_launch_arg,
        open_trigger_topic_launch_arg,
        grasp_trigger_topic_launch_arg,
        action_command_topic_launch_arg,
        debug_launch_arg,
        prensilia_control_node, 
    ])
