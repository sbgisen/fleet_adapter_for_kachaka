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


class RobotAPI:
    # The constructor below accepts parameters typically required to submit
    # http requests. Users should modify the constructor as per the
    # requirements of their robot's API
    def __init__(self, config_yaml: dict) -> None:
        self.prefix = config_yaml['prefix']
        self.user = config_yaml['user']
        self.password = config_yaml['password']
        self.timeout = 5.0
        self.debug = False

    def check_connection(self) -> bool:
        ''' Return True if connection to the robot API server is successful '''
        url = self.prefix + "kachaka/get_robot_serial_number"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def navigate(
        self,
        robot_name: str,
        pose: list[float],
        map_name: str,
        speed_limit: float = 0.0
    ) -> bool:
        ''' Request the robot to navigate to pose:[x,y,theta] where x, y and
            and theta are in the robot's coordinate convention. This function
            should return True if the robot has accepted the request,
            else False '''
        url = self.prefix + "kachaka/set_robot_velocity"
        if speed_limit == 0.0:
            velocity = {"linear": 1.0, "angular": 1.0}
        else:
            velocity = {"linear": speed_limit, "angular": 1.0}
        response = requests.post(url, json=velocity)

        url = self.prefix + "kachaka/move_to_pose"
        position = {"x": pose[0], "y": pose[1], "yaw": pose[2]}
        try:
            response = requests.post(url, json=position)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def start_activity(
        self,
        robot_name: str,
        activity: str,
        label: str
    ) -> bool:
        ''' Request the robot to begin a process. This is specific to the robot
        and the use case. For example, load/unload a cart for Deliverybot
        or begin cleaning a zone for a cleaning robot.
        Return True if process has started/is queued successfully, else
        return False '''
        print(f"start activity. {activity}_command, {label}")
        if activity == "pickup":
            url = self.prefix + "kachaka/dock_shelf"
            shelf = {"title": 'S01'}
            # TODO shelf = {"title": f"{label}"}

        elif activity == "dropoff":
            url = self.prefix + "kachaka/undock_shelf"
            shelf = {"title": 'S01'}
            # TODO shelf = {"title": f"{label}"}
        else:
            return False
        try:
            response = requests.post(url, json=shelf)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def stop(self, robot_name: str) -> bool:
        ''' Command the robot to stop.
            Return True if robot has successfully stopped. Else False. '''
        url = self.prefix + "kachaka/cancel_command"
        try:

            response = requests.get(url)
            res = response.json()
            if res['success']:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def position(self, robot_name: str) -> list[float] | None:
        ''' Return [x, y, theta] expressed in the robot's coordinate frame or
        None if any errors are encountered '''
        url = self.prefix + "kachaka/get_robot_pose"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                res = response.json()
                return [res['x'], res['y'], res['theta']]
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def battery_soc(self, robot_name: str) -> float | None:
        ''' Return the state of charge of the robot as a value between 0.0
        and 1.0. Else return None if any errors are encountered. '''
        # Now submit a request to make API
        # ------------------------ #
        # IMPLEMENT YOUR CODE HERE #
        # ------------------------ #
        return 0.8

    def map(self, robot_name: str) -> str | None:
        ''' Return the name of the map that the robot is currently on or
        None if any errors are encountered. '''
        url = self.prefix + "kachaka/get_png_map"
        try:
            response = requests.get(url)
            res = response.json()
            if response.status_code == 200:
                return "L1"
                # TODO return res['name']
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def is_command_completed(self) -> bool:
        ''' Return True if the robot has completed its last command, else
        return False. '''
        url = self.prefix + "kachaka/get_last_command_result"
        try:
            response = requests.get(url)
            res = response.json()
            if res[0]['success']:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def get_data(self, robot_name: str):
        ''' Returns a RobotUpdateData for one robot if a name is given. Otherwise
        return a list of RobotUpdateData for all robots. '''
        map = self.map(robot_name)
        position = self.position(robot_name)
        battery_soc = self.battery_soc(robot_name)
        if not (map is None or position is None or battery_soc is None):
            return RobotUpdateData(robot_name, map, position, battery_soc)
        return None


class RobotUpdateData:
    ''' Update data for a single robot. '''

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
