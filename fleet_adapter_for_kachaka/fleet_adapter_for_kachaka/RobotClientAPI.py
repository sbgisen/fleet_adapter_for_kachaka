#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import requests

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


'''
    The RobotAPI class is a wrapper for API calls to the robot. Here users
    are expected to fill up the implementations of functions which will be used
    by the RobotCommandHandle. For example, if your robot has a REST API, you
    will need to make http request calls to the appropriate endpoints within
    these functions.
'''


class RobotUpdateData:
    """ Update data for a single robot. """

    def __init__(self,
                 robot_name: str,
                 map: str,
                 position: list[float],
                 battery_soc: float,
                 requires_replan: bool | None = None) -> None:
        self.robot_name = robot_name
        self.position = position
        self.map = map
        self.battery_soc = battery_soc
        self.requires_replan = requires_replan


class RobotAPI:
    """ Provides methods for interacting with the robot fleet manager API. """

    def __init__(self, config_yaml: dict) -> None:
        self.prefix = config_yaml['prefix']
        self.user = config_yaml['user']
        self.password = config_yaml['password']
        self.timeout = 5.0
        self.debug = False
        self.task_id = ""

    def check_connection(self) -> bool:
        ''' Return True if connection to the robot API server is successful '''
        url = self.prefix + "kachaka/**"
        try:
            response = requests.get(url)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            print("Connection error")
            return False

    def navigate(
        self,
        robot_name: str,
        pose: list[float],
        map_name: str,
        speed_limit: float = 0.0
    ) -> bool:
        """Send navigation request to robot."""
        url = f"{self.prefix}kachaka/{robot_name}/command"

        velocity = {'linear': speed_limit or 1.0, 'angular': 1.0}
        self._delete_command_state(robot_name)
        requests.put(
            url, json={'method': 'set_robot_velocity', 'args': velocity})

        position = {'x': pose[0], 'y': pose[1], 'yaw': pose[2]}
        self._delete_command_state(robot_name)
        response = requests.put(
            url, json={'method': 'move_to_pose', 'args': position})

        self.task_id = response.json()['id']
        return response.status_code == 200

    def start_activity(
        self,
        robot_name: str,
        activity: str,
        label: str
    ) -> bool:
        """Send activity request to robot."""
        if activity != "dock":
            return False

        url = f"{self.prefix}kachaka/{robot_name}/command"
        self._delete_command_state(robot_name)
        response = requests.put(
            url, json={'method': 'return_home', 'args': {}})
        self.task_id = response.json()['id']
        return response.status_code == 200

    def _delete_command_state(self, robot_name: str) -> None:
        """Clear existing command state for robot."""
        url = f"{self.prefix}kachaka/{robot_name}/command_state"
        requests.delete(url)

    def stop(self, robot_name: str) -> bool:
        """Send stop request to robot."""
        url = f"{self.prefix}kachaka/{robot_name}/command"
        self._delete_command_state(robot_name)
        response = requests.put(
            url, json={'method': 'cancel_command', 'args': {}})
        return response.json().get('success', False)

    def position(self, robot_name: str) -> list[float] | None:
        """Get current position of robot."""
        url = f"{self.prefix}kachaka/{robot_name}/pose"
        response = requests.get(url)
        if response.status_code != 200:
            return None

        data = response.json()[0]['value']
        return [data['x'], data['y'], data['theta']]

    def battery_soc(self, robot_name: str) -> float | None:
        """Get robot's battery state of charge. Not yet implemented."""
        ''' Return the state of charge of the robot as a value between 0.0
        and 1.0. Else return None if any errors are encountered. '''
        # TODO: The battery_soc is not implemented in the API
        return 0.8

    def map(self, robot_name: str) -> str | None:
        """Get name of map the robot is currently on."""
        url = f"{self.prefix}kachaka/{robot_name}/map_name"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            map_name = data[0]['value']
            return "L1"
        else:
            return None

    def is_command_completed(self, robot_name: str) -> bool:
        """Check if robot's last command has finished executing."""
        url = f"{self.prefix}kachaka/{robot_name}/command_state"
        response = requests.get(url)
        if response.status_code != 200:
            return False

        state = response.json()[0]['value'][0]  # 1: waiting for requests
        return state == 1

    def get_data(self, robot_name: str) -> RobotUpdateData | None:
        """Get update data for the specified robot.

        Returns:
            RobotUpdateData object if successful, None if errors.
        """
        map = self.map(robot_name)
        position = self.position(robot_name)
        battery_soc = self.battery_soc(robot_name)
        if map is None or position is None or battery_soc is None:
            return None
        return RobotUpdateData(robot_name, map, position, battery_soc)
