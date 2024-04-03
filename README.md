# fleet_adapter_template

> Note: If you are using Open-RMF binaries from ROS 2 Humble or an older distribution, switch to the [humble](https://github.com/open-rmf/fleet_adapter_template/tree/humble) branch.

The objective of this package is to serve as a reference or template for writing a python based `full_control` RMF fleet adapter.

> Note: The implementation in this package is not the only way to write a `full_control` fleet adapter. It is only one such example that may be helpful for users to quickly integrate their fleets with RMF.


## Step 1: Setup Kachaka

Using [forked Kachaka-api](https://github.com/h-wata/kachaka-api/blob/feature/rest_api_wrapper/python/demos/url_kachaka_api.ipynb), run the REST API.

```bash
export KACHAKA_IP=192.168.XX.YY
ssh -p 26500 -l kachaka $KACHAKA_IP
cd kachaka-api
git remote add h-wata https://github.com:h-wata/feature/rest_api_wrapper
git pull feature/rest_api_wrapper
```

Please run `python/demos/url_kachaka_api.ipynb` in Jupyter Notebook.

## Step 2: Update config.yaml
The `config.yaml` file contains important parameters for setting up the fleet adapter. There are three broad sections to this file:

1. **rmf_fleet** : containing parameters that describe the robots in this fleet
2. **fleet_manager** : containing configurations to connect to the robot's API in order to retrieve robot status and send commands from RMF
3. **reference_coordinates**: containing two sets of [x,y] coordinates that correspond to the same locations but recorded in RMF (`traffic_editor`) and robot specific coordinates frames respectively. These are required to estimate coordinate transformations from one frame to another. A minimum of 4 matching waypoints is recommended.

> Note: This fleet adapter uses the `nudged` python library to compute transformations from RMF to Robot frame and vice versa. If the user is aware of the `scale`, `rotation` and `translation` values for each transform, they may modify the code in `fleet_adapter.py` to directly create the `nudged` transform objects from these values.

## Step 3: Run the fleet adapter:

Run the command below while passing the paths to the configuration file and navigation graph that this fleet operates on.

The websocket server URI should also be passed as a parameter in this command inorder to publish task statuses to the rest of the RMF entities.

```bash
#minimal required parameters
ros2 run fleet_adapter_kachaka fleet_adapter -c CONFIG_FILE -n NAV_GRAPH

#Usage with the websocket uri
ros2 run fleet_adapter_kachaka template fleet_adapter -c CONFIG_FILE -n NAV_GRAPH -s SERVER_URI

#e.g.
ros2 run fleet_adapter_kachaka template fleet_adapter -c CONFIG_FILE -n NAV_GRAPH -s ws://localhost:7878
```
