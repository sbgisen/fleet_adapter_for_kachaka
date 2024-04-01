#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# Copyright (c) 2023 SoftBank Corp.
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

import yaml


def get_user_input(prompt: str, default: str = None) -> str:
    if default:
        user_input = input(f"{prompt} (default: {default}): ")
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ")


# Load the existing config_template.yaml
with open('config_template.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Configure fleet_manager
config['fleet_manager'] = {}
config['fleet_manager']['prefix'] = get_user_input(
    "Fleet Manager prefix", "http://192.168.1.100:26502/")
config['fleet_manager']['user'] = get_user_input(
    "Fleet Manager username", "some_user")
config['fleet_manager']['password'] = get_user_input(
    "Fleet Manager password", "some_password")

# Configure reference_coordinates
config['reference_coordinates'] = {}
while True:
    location_name = get_user_input(
        "Location name for coordinates (enter 'q' to finish)")
    if location_name == 'q':
        break
    config['reference_coordinates'][location_name] = {}
    config['reference_coordinates'][location_name]['rmf'] = []
    config['reference_coordinates'][location_name]['robot'] = []

    print(
        f"Enter at least 4 RMF coordinates for {location_name} (enter 'q' to finish)")
    while True:
        rmf_coord = get_user_input("RMF coordinate (e.g., 25.4962, -9.0341)")
        if rmf_coord == 'q':
            break
        rmf_x, rmf_y = map(float, rmf_coord.split(','))
        config['reference_coordinates'][location_name]['rmf'].append([
                                                                     rmf_x, rmf_y])

    print(
        f"Enter at least 4 robot coordinates for {location_name} (enter 'q' to finish)")
    while True:
        robot_coord = get_user_input("Robot coordinate (e.g., 0.679, 1.447)")
        if robot_coord == 'q':
            break
        robot_x, robot_y = map(float, robot_coord.split(','))
        config['reference_coordinates'][location_name]['robot'].append([
                                                                       robot_x, robot_y])

# Get the output file name
output_file = get_user_input(
    "Enter the output file name (e.g., config_custom.yaml)")

# Write the configuration to the YAML file
with open(output_file, 'w') as file:
    yaml.dump(config, file)

print(f"Configuration completed. Please check the {output_file} file.")
