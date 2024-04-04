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

import getpass

import yaml


def get_user_input(prompt: str, default: str = None) -> str:
    if default:
        user_input = input(f"{prompt} (default: {default}): ")
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ")


# Load the existing config_template.yaml
try:
    with open('config_template.yaml', 'r') as file:
        config = yaml.safe_load(file)
except yaml.YAMLError as exc:
    print(f"Error loading YAML file: {exc}")
    exit(1)
except FileNotFoundError:
    print("config_template.yaml not found. Try running this script from the correct directory.")
    exit(1)

# Configure fleet_manager
config['fleet_manager'] = {}
config['fleet_manager']['prefix'] = get_user_input(
    "Fleet Manager prefix", "http://192.168.1.100:26502/")
config['fleet_manager']['user'] = get_user_input(
    "Fleet Manager username", "some_user")
config['fleet_manager']['password'] = getpass.getpass(
    "Fleet Manager password (default: some_password): ") or "some_password"
# Configure reference_coordinates
config['reference_coordinates'] = {}
while True:
    level_name = get_user_input(
        "Level name for coordinates (enter 'q' to finish)")
    if level_name == 'q':
        break
    config['reference_coordinates'][level_name] = {}
    config['reference_coordinates'][level_name]['rmf'] = []
    config['reference_coordinates'][level_name]['robot'] = []
    print(f"RMF coordinates for level: {level_name} (at least 2 required, 4 recommended) (enter 'q' to finish)")
    count = 0
    while True:
        rmf_coord = get_user_input("RMF coordinate (e.g., 25.4962, -9.0341)")
        if rmf_coord == 'q':
            if count < 2:
                print("Please enter at least 2 RMF coordinates.")
                continue
            break
        rmf_x, rmf_y = map(float, rmf_coord.split(','))
        config['reference_coordinates'][level_name]['rmf'].append([rmf_x, rmf_y])
        count += 1
    print(f"Robot coordinates for level: {level_name} (same number as RMF coordinates required)")
    while count > 0:
        robot_coord = get_user_input("Robot coordinate (e.g., 0.679, 1.447)")
        try:
            robot_x, robot_y = map(float, robot_coord.split(','))
        except ValueError:
            print("Invalid input. Please try again.")
            continue
        config['reference_coordinates'][level_name]['robot'].append([robot_x, robot_y])
        count -= 1

while True:
    # Get the output file name
    output_file = get_user_input(
        "Enter the output file name (e.g., config_custom.yaml)", "config_custom.yaml")
    try:
        # Write the configuration to the YAML file
        with open(output_file, 'w') as file:
            yaml.safe_dump(config, file)
        break
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error: {e}. Please try again.")

print(f"Configuration completed. Please check the {output_file} file.")
