# fleet_adapter_kachaka

Open-RMF fleet adapter for Kachaka robot.
All scripts are tested under the Ubuntu 22.04 and ROS2 Humble environment.

## Step 1: Setup REST API server for Kachaka

This adapter utilizes the REST API version of the Kachaka API. To run the adapter, the REST API must be running and accessible.

Clone [kachaka-api-for-openrmf](https://github.com/sbgisen/kachaka-api-for-openrmf) to your workspace and follow the instruction [here](https://github.com/sbgisen/kachaka-api-for-openrmf/blob/main/README.md#setup-kachaka-internal-components) to setup the Kachaka REST API server.

## Step 2: Update config.yaml

The `config.yaml` file contains important parameters for setting up the fleet adapter. There are three broad sections to this file:

1. **rmf_fleet** : containing parameters that describe the robots in this fleet
2. **fleet_manager** : containing configurations to connect to the robot's API in order to retrieve robot status and send commands from RMF
3. **reference_coordinates**: containing two sets of [x,y] coordinates that correspond to the same locations but recorded in RMF (`traffic_editor`) and robot specific coordinates frames respectively. These are required to estimate coordinate transformations from one frame to another. A minimum of 4 matching waypoints is recommended.

## Step 3: Run the fleet adapter

Run the command below while passing the paths to the configuration file and navigation graph that this fleet operates on.

The web socket server URI should also be passed as a parameter in this command to publish task statuses to the rest of the RMF entities.

```bash
# minimal required parameters
ros2 run fleet_adapter_kachaka fleet_adapter -c CONFIG_FILE -n NAV_GRAPH

# Usage with the websocket uri
ros2 run fleet_adapter_kachaka fleet_adapter -c CONFIG_FILE -n NAV_GRAPH -s SERVER_URI

# e.g.
ros2 run fleet_adapter_kachaka fleet_adapter -c CONFIG_FILE -n NAV_GRAPH -s ws://localhost:7878
```
