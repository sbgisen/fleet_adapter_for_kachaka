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

    def __init__(self, robot_name: str, map: str, position: list[float], battery_soc: float,
                 requires_replan: bool | None = None) -> None:
        self.robot_name = robot_name
        self.position = position
        self.map = map
        self.battery_soc = battery_soc
        self.requires_replan = requires_replan


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
        url = self.prefix + "kachaka/get_robot_serial_number"
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
        # Set linear velocity based on speed limit
        linear_velocity = speed_limit if speed_limit > 0.0 else 1.0
        velocity = {"linear": linear_velocity, "angular": 1.0}

        url = self.prefix + "kachaka/set_robot_velocity"
        requests.post(url, json=velocity)

        url = self.prefix + "kachaka/move_to_pose"
        position = {"x": pose[0], "y": pose[1], "yaw": pose[2]}
        try:
            response = requests.post(url, json=position)
            self.task_id = response.json()['id']
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error in navigate request: {e}")
            return False

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

        url = self.prefix + "kachaka/return_home"
        try:
            response = requests.post(url, json={})
            self.task_id = response.json()['id']
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error starting activity: {e}")
            return False

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
        url = self.prefix + "kachaka/cancel_command"
        try:
            response = requests.get(url)
            return response.json()['success']
        except requests.RequestException as e:
            print(f"Error stopping robot: {e}")
            return False

    def position(self, robot_name: str) -> list[float] | None:
        """
        Get the current position of the robot.

        Args:
            robot_name (str): The name of the robot.

        Returns:
            list[float] | None: The current position as [x, y, theta], or None if an error occurred.
        """
        url = self.prefix + "kachaka/get_robot_pose"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                res = response.json()
                return [res['x'], res['y'], res['theta']]
            else:
                return None
        except requests.RequestException as e:
            print(f"Error getting robot position: {e}")
            return None

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
        return 0.8

    def map(self, robot_name: str) -> str | None:
        """
        Get the name of the map the robot is currently on.

        Args:
            robot_name (str): The name of the robot.

        Returns:
            str | None: The name of the current map, or None if an error occurred.
        """
        try:
            map_list_url = self.prefix + "kachaka/get_map_list"
            map_list_response = requests.get(map_list_url)

            if map_list_response.status_code != 200:
                return None

            map_list = map_list_response.json()
            if not map_list:
                return None

            current_map_url = self.prefix + "kachaka/get_current_map_id"
            current_map_response = requests.get(current_map_url)

            if current_map_response.status_code != 200:
                return None

            current_map_id = current_map_response.json()
            current_map = next(
                (m for m in map_list if m["id"] == current_map_id), None)

            return current_map['name'] if current_map else "L1"
        except requests.RequestException as e:
            print(f"Error getting current map: {e}")
            return None

    def is_command_completed(self) -> bool:
        """
        Check if the robot has completed its last command.

        Returns:
            bool: True if the last command has been completed, False otherwise.
        """
        url = self.prefix + f"command_result?task_id={self.task_id}"
        try:
            response = requests.get(url)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error checking command status: {e}")
            return False

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
