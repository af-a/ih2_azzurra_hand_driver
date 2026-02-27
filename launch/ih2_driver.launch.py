#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    serial_port_launch_arg = DeclareLaunchArgument(
        'serial_port', 
        default_value='/dev/ttyUSB0',
        description='TODO'
    )
    pose_config_file_path_launch_arg = DeclareLaunchArgument(
        'pose_config_file_path', 
        default_value='/home/ahmed/workspace/ros2_ws/src/ih2_azzurra_hand_driver/config/default_hand_poses.yaml',
        description='TODO'
    )

    prensilia_control_node_name = 'new_driver_node'
    prensilia_control_node = Node(
        package='ih2_azzurra_hand_driver',
        executable='new_driver_node',
        name=prensilia_control_node_name,
        parameters=[
            {'serial_port': LaunchConfiguration('serial_port')},
            {'pose_config_file_path': LaunchConfiguration('pose_config_file_path')},
        ],
        on_exit=Shutdown(),
    )

    rqt_reconfigure_node = Node(
        package='rqt_reconfigure',
        executable='rqt_reconfigure',
        name='ih2_rqt_reconfigure',
        arguments=[f'/{prensilia_control_node_name}'],
    )

    return LaunchDescription([
        serial_port_launch_arg,
        pose_config_file_path_launch_arg,
        prensilia_control_node, 
        rqt_reconfigure_node,
    ])
