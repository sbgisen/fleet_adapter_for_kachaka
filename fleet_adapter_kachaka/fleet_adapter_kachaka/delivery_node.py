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

import argparse
import sys
import time

import rclpy
import requests
import yaml
from rclpy.node import Node
from rmf_dispenser_msgs.msg import DispenserRequest
from rmf_dispenser_msgs.msg import DispenserResult
from rmf_ingestor_msgs.msg import IngestorRequest
from rmf_ingestor_msgs.msg import IngestorResult

from .RobotClientAPI import RobotAPI


def main(argv: list[str] | None = sys.argv) -> None:
    # Init rclpy and adapter
    rclpy.init(args=argv)
    args_without_ros = rclpy.utilities.remove_ros_args(argv)

    parser = argparse.ArgumentParser(
        prog="fleet_adapter",
        description="Configure delivery node for the fleet adapter")
    parser.add_argument("-c", "--config_file", type=str, required=True,
                        help="Path to the config.yaml file")
    args = parser.parse_args(args_without_ros[1:])

    config_path = args.config_file
    # get config path from rclpy
    # Parse the yaml in Python to get the fleet_manager info
    with open(config_path, "r") as f:
        config_yaml = yaml.safe_load(f)
    # Initialize robot API for this fleet
    node = DeliveryNode(config_yaml)
    rclpy.spin(node)
    rclpy.shutdown()


class DeliveryNode(Node):
    def __init__(self, config_yaml: dict) -> None:
        super().__init__('delivery_node')
        self.docked = False
        self.config_yaml = config_yaml['fleet_manager']
        self.fleet_name = config_yaml['rmf_fleet']['name']
        self.get_logger().info(f"fleet name is {self.fleet_name}")
        self.robot_api = RobotAPI(self.config_yaml)

        # Subcribe to dispenser_requests
        self.dispenser_request_sub = self.create_subscription(
            DispenserRequest,
            'dispenser_requests',
            self.dispenser_request_callback,
            10
        )

        # publish to despenser reaults
        self.dispenser_result_pub = self.create_publisher(
            DispenserResult,
            'dispenser_results',
            10
        )
        # subscribe to ingestor_requests
        self.ingestor_request_sub = self.create_subscription(
            IngestorRequest,
            'ingestor_requests',
            self.ingestor_request_callback,
            10
        )
        # publish to ingestor results
        self.ingestor_result_pub = self.create_publisher(
            IngestorResult,
            'ingestor_results',
            10
        )
        self.get_logger().info("Delivery node is ready")

    # Callback function for dispenser_requests
    def dispenser_request_callback(self, msg: DispenserRequest) -> None:
        # check if the transporter type is the same as the fleet name
        if msg.transporter_type != self.fleet_name:
            return
        self.get_logger().info("Received dispenser request")
        if not self.docked:
            pub_msg = DispenserResult()
            if self.start_action("pickup"):
                pub_msg.status = DispenserResult.SUCCESS
                self.docked = True
            else:
                pub_msg.status = DispenserResult.FAILED
                self.docked = False
            self.get_logger().info("Sending dispenser result")
            pub_msg.time = self.get_clock().now().to_msg()
            pub_msg.request_guid = msg.request_guid
            pub_msg.source_guid = msg.target_guid
            self.dispenser_result_pub.publish(pub_msg)
        else:
            self.get_logger().info("Already docked. Cannot pickup")
            return

    # Callback function for ingestor_requests
    def ingestor_request_callback(self, msg: IngestorRequest) -> None:
        # check if the transporter type is the same as the fleet name
        if msg.transporter_type != self.fleet_name:
            return
        self.get_logger().info("Received ingestor request")
        if self.docked:
            pub_msg = IngestorResult()
            if self.start_action("dropoff"):
                pub_msg.status = IngestorResult.SUCCESS
                self.docked = False
            else:
                pub_msg.status = IngestorResult.FAILED
                self.docked = True
            pub_msg.time = self.get_clock().now().to_msg()
            pub_msg.request_guid = msg.request_guid
            pub_msg.source_guid = msg.target_guid
            self.get_logger().info("Sending ingesto result")
            self.ingestor_result_pub.publish(pub_msg)
        else:
            self.get_logger().info("Not docked. Cannot dropoff")
            return

    def start_action(
        self,
        action: str,
    ) -> bool:
        print(f"start action. {action}_command")
        if action == "pickup":
            url = self.robot_api.prefix + "kachaka/dock_shelf"
            shelf = {"title": ""}

        elif action == "dropoff":
            url = self.robot_api.prefix + "kachaka/undock_shelf"
            shelf = {"title": ""}
        else:
            return False
        try:
            # TODO 成否を問う。成功したらTrueを返すようにする。
            response = requests.post(url, json=shelf)
            self.task_id = response.json()["id"]
            if response.status_code == 200:
                while self.completed_action() is False:
                    time.sleep(1)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def completed_action(self) -> bool:
        url = self.robot_api.prefix + f"command_result?task_id={self.task_id}"
        task = {"id": self.task_id}
        try:
            response = requests.post(url, json=task)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False


if __name__ == "__main__":
    main(argv=sys.argv)
