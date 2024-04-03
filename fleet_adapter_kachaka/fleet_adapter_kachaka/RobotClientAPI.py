#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# Copyright (c) 2024 SoftBank Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Copyright 2021 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests


class RobotUpdateData:
    """
    Class representing update data for a single robot.

    Attributes:
        robot_name (str): The name of the robot.
        map (str): The name of the map the robot is on.
        position (list[float]): The position of the robot as [x, y, theta].
        battery_soc (float): The state of charge of the robot's battery.
        requires_replan (bool | None): Whether the robot requires replanning.
    """

    def __init__(self, robot_name: str, map: str, position: list[float], battery_soc: float
                 | None = None) -> None:
        self.robot_name = robot_name
        self.position = position
        self.map = map
        self.battery_soc = battery_soc
        # self.requires_replan = requires_replan


class RobotAPI:
    """
    Class providing a wrapper for API calls to the robot.

    Attributes:
        prefix (str): The URL prefix for the robot API.
        user (str): The username for authenticating with the robot API.
        password (str): The password for authenticating with the robot API.
        timeout (float): The timeout in seconds for API requests.
        debug (bool): Whether to print debug information.
        task_id (str): The ID of the current task.
    """

    def __init__(self, config_yaml: dict) -> None:
        """
        Initialize a new RobotAPI instance.

        Args:
            config_yaml (dict): A dictionary containing configuration parameters.
        """
        self.prefix = config_yaml['prefix']
        self.user = config_yaml['user']
        self.password = config_yaml['password']
        self.timeout = 5.0
        self.debug = False
        self.task_id = ""

    def check_connection(self) -> bool:
        """
        Check if the connection to the robot API server is successful.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        url = self.prefix + "get_robot_serial_number"
        try:
            response = requests.get(url, timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def navigate(self, robot_name: str, pose: list[float], map_name: str, speed_limit: float = 0.0) -> bool:
        """
        Request the robot to navigate to the specified pose.

        Args:
            robot_name (str): The name of the robot.
            pose (list[float]): The target pose as [x, y, theta].
            map_name (str): The name of the map to navigate on.
            speed_limit (float): The maximum speed for navigation. Default is 0.0.

        Returns:
            bool: True if the navigation request is successful, False otherwise.
        """
        url = f"{self.prefix}{robot_name}/command"
        velocity = {'linear': speed_limit or 1.0, 'angular': 1.0}
        self._delete_command_state(robot_name)
        requests.put(
            url, json={'method': 'set_robot_velocity', 'args': velocity})

        position = {'x': pose[0], 'y': pose[1], 'yaw': pose[2]}
        self._delete_command_state(robot_name)
        response = requests.put(
            url, json={'method': 'move_to_pose', 'args': position})

        # self.task_id = response.json()['id']
        return response.status_code == 200

    def start_activity(self, robot_name: str, activity: str, label: str) -> bool:
        """
        Request the robot to begin a specified activity.

        Args:
            robot_name (str): The name of the robot.
            activity (str): The type of activity to start. Currently only supports "dock".
            label (str): An optional label for the activity.

        Returns:
            bool: True if the activity request is successful, False otherwise.
        """
        if activity != "dock":
            return False

        url = f"{self.prefix}{robot_name}/command"
        self._delete_command_state(robot_name)
        response = requests.put(
            url, json={'method': 'return_home', 'args': {}})
        # self.task_id = response.json()['id']
        return response.status_code == 200

    def _delete_command_state(self, robot_name: str) -> None:
        """Clear existing command state for robot."""
        url = f"{self.prefix}{robot_name}/command_state"
        requests.delete(url)

    def get_task_id(self) -> str:
        """
        Get the ID of the current task.

        Returns:
            str: The ID of the current task.
        """
        return self.task_id

    def stop(self, robot_name: str) -> bool:
        """
        Command the robot to stop.

        Args:
            robot_name (str): The name of the robot.

        Returns:
            bool: True if the stop command is successful, False otherwise.
        """
        url = f"{self.prefix}{robot_name}/command"
        self._delete_command_state(robot_name)
        response = requests.put(
            url, json={'method': 'cancel_command', 'args': {}})
        return response.json().get('success', False)

    def position(self, robot_name: str) -> list[float] | None:
        """
        Get the current position of the robot.

        Args:
            robot_name (str): The name of the robot.

        Returns:
            list[float] | None: The current position as [x, y, theta], or None if an error occurred.
        """
        url = f"{self.prefix}{robot_name}/pose"
        response = requests.get(url)
        if response.status_code != 200:
            return None

        data = response.json()[0]['value']
        return [data['x'], data['y'], data['theta']]

    def battery_soc(self, robot_name: str) -> float | None:
        # TODO: Implement battery_soc in the robot API
        """
        Get the state of charge of the robot's battery.

        Args:
            robot_name (str): The name of the robot.

        Returns:
            float | None: The state of charge as a percentage between 0 and 100, or None if not available.

        Notes:
            - This method is not yet implemented in the robot API and always returns a placeholder value.
        """
        url = f"{self.prefix}{robot_name}/battery"
        response = requests.get(url)
        if response.status_code != 200:
            return None

        data = response.json()[0]['value']
        # return data
        return 0.8

    def map(self, robot_name: str) -> str | None:
        """
        Get the name of the map the robot is currently on.

        Args:
            robot_name (str): The name of the robot.

        Returns:
            str | None: The name of the current map, or None if an error occurred.
        """
        url = f"{self.prefix}{robot_name}/map_name"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            map_name = data[0]['value']
            return "L1"
        else:
            return None

    def is_command_completed(self, robot_name: str) -> bool:
        """
        Check if the robot has completed its last command.

        Returns:
            bool: True if the last command has been completed, False otherwise.
        """
        url = f"{self.prefix}{robot_name}/command_state"
        response = requests.get(url)
        if response.status_code != 200:
            return False

        state = response.json()[0]['value'][0]  # 1: waiting for requests
        return state == 1

    def get_data(self, robot_name: str) -> RobotUpdateData | None:
        """
        Get the latest update data for the specified robot.

        Args:
            robot_name (str): The name of the robot.

        Returns:
            RobotUpdateData | None: The latest update data for the robot, or None if an error occurred.
        """
        map_name = self.map(robot_name)
        position = self.position(robot_name)
        battery_soc = self.battery_soc(robot_name)

        if map_name is None or position is None or battery_soc is None:
            return None
        return RobotUpdateData(robot_name, map_name, position, battery_soc)
