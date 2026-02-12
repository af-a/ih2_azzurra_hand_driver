
<div align="center">

A ROS package that exposes the control interfaces of the [Prensilia IH2 Azzurra Hand](https://www.prensilia.com/ih2-azzurra-hand/).

Designed for and tested on Ubuntu 22.04 LTS, ROS (2) Humble with Python 3.10.

<!-- Note on dev stage
-->
<b>Note: The package is in an initial development phase. It is unstable and may significantly change in concept and implementation.</b>
  
[![Python 3.10](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<b>Author:</b> [Ahmed Abdelrahman](https://github.com/af-a)

</div>

## Contents
- [➤ Overview](#overview)
- [➤ Installation](#installation)
- [➤ Usage](#usage)
- [➤ Directory Structure](#directory-structure)
- [➤ Dependencies](#dependencies)
- [➤ Future Plans](#future-plans)

## Overview

TODO

## Installation

### Build Package

After cloning this repository in your workspace, build the package using:
```
colcon build --packages-select ih2_azzurra_hand_driver
```

## Usage

TODO

To execute a tri-grasp with the Prensilia hand:
```bash
ros2 topic pub --once /prensilia_control_node/action_command std_msgs/msg/String "{'data': 'tri_grasp'}"
```

To open the Prensilia hand:
```bash
ros2 topic pub --once /prensilia_control_node/action_command std_msgs/msg/String "{'data': 'open'}"
```

To execute a more gradual opening of the Prensilia hand from a tri-grasp position (for more delicate object release):
```bash
ros2 topic pub --once /prensilia_control_node/action_command std_msgs/msg/String "{'data': gradual_open_tri_grasp_objects}"
```


## Directory Structure

<details>
<summary> Package Files </summary>

```
ih2_azzurra_hand_driver
│
├── ih2_azzurra_hand_driver
│   ├── __init__.py
│   ├── prensilia_control_node.py
│   └── prensilia_hand_control.py
│
├── launch
│   └── prensilia_control.launch.py
│
├── config
├── LICENSE
├── package.xml
├── README.md
├── resource
├── setup.cfg
└── setup.py
```

</details>

## Dependencies

Python:
* `pyserial`

ROS:
* `rclpy`
* `ament_cmake_python`
* `std_msgs`

## Future Plans

- [ ] Add publishing of current hand information (joint angles, current, etc.) in standardized ROS messages
- [ ] Add feature: read hand pose definitions for YAML files
- [ ] Add feature: continuous control of individual DoAs through ROS topics
- [ ] Add feature: a GUI plugin thtat exposes and enables control of variables

<!-- TODO: Add references, etc., if any
## Credits
* ...
 -->
