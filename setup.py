#!/usr/bin/env python3

import os
import glob

from setuptools import setup, find_packages

package_name = "ih2_azzurra_hand_driver"

setup(
    name=package_name,
    version="0.1.0",
    description="""Exposes interfaces to the Prensilia IH2 Azzurra Hand""",
    author="Ahmed Abdelrahman",
    author_email="ahmed.abdelrahman@outlook.de",
    maintainer="Ahmed Abdelrahman",
    maintainer_email="ahmed.abdelrahman@outlook.de",
    packages=find_packages(include=[package_name]),
    license="MIT",
    install_requires=[
        "rclpy",
        "std-msgs",
        "sensor-msgs",
        "pyserial",
    ],
    setup_requires=["wheel"],
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        (os.path.join('share', package_name, 'launch'), glob.glob(os.path.join('launch', '*launch.[pxy][yma]*')))
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
    ],
    keywords=[
        "Prensilia",
        "IH2 Azzurra",
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'driver_node = ih2_azzurra_hand_driver.prensilia_control_node:main'
        ],
    },
)
