"""
# ------------------------------------------------------------------------------------------------------------------------
# CT APIs
# ------------------------------------------------------------------------------------------------------------------------
"""

import requests
import json
import Properties
import Authenticate

##############################################
HOSTNAME = Properties.Properties.HOSTNAME
COMPS_PATH = Properties.Properties.COMPS_PATH
GRID_NAME = Properties.Properties.GRID_NAME
##############################################

"""
# Get Grid Id done
# Start the Grid done
# Check status of the grid done
# Load the composition done
# Play Loaded Composition done
# stop the composition done
# Terminate the Grid done
# Pull Results
"""


def GetGridId(header, HOSTNAME, GRID_NAME):
    try:
        url = f"{HOSTNAME}/concerto/services/rest/RepositoryService/v1/Objects/grid?name={GRID_NAME}"
        response = requests.get(url, headers=header, verify=False)
        response.raise_for_status()  # Raises an exception for 4xx and 5xx status codes
        print(f"INFO: Get Grid Id for '{GRID_NAME}'")
        return response.json()["objects"][0]["id"]
    except Exception as e:
        print(f"ERROR: Unable to get the Grid ID! {e}")


def StartGrid(header, HOSTNAME, grid_id):
    try:
        url = f"{HOSTNAME}/concerto/services/rest/CloudService/v1/grid/{grid_id}/action"
        response = requests.post(
            url, json={"action": "start"}, headers=header, verify=False
        )
        response.raise_for_status()
        print("INFO: Starting the Grid '" + GRID_NAME + "'.")
    except Exception as e:
        print(f"ERROR: Unable to start the Grid! {e}")


def CheckGridStatus(header, HOSTNAME, grid_id):
    try:
        url = f"{HOSTNAME}/concerto/services/rest/CloudService/v1/grid/{grid_id}"
        response = requests.get(url, headers=header, verify=False)
        response.raise_for_status()
        return response.json()["state"]
    except Exception as e:
        print(f"ERROR: Unable to get the status of the Grid!")


def LoadComposition(header, HOSTNAME, COMPS_PATH):
    try:
        url = f"{HOSTNAME}/concerto/services/rest/composition/instances/v1?command=load"
        response = requests.post(
            url, headers=header, json={"compositionName": COMPS_PATH}, verify=False
        )
        response.raise_for_status()
        return response.json()["instanceID"]
    except Exception as e:
        error_msg = str(response.json()["message"])
        print(
            f"ERROR: Loading Composition Failed for {COMPS_PATH} - {error_msg} ")


def PlayComposition(header, HOSTNAME, instance_id, COMPS_PATH):
    try:
        url = f"{HOSTNAME}/concerto/services/rest/composition/instances/v1/{instance_id}?command=play"
        response = requests.put(
            url, json={"compositionName": COMPS_PATH}, headers=header, verify=False
        )
        response.raise_for_status()
        return response.json()["instanceID"]
    except Exception as e:
        error_msg = str(response.json()["message"])
        print(
            f"ERROR: An error occurred when tried to play the composition {COMPS_PATH}, {error_msg}"
        )


def StopComposition(header, HOSTNAME, instance_id, COMPS_PATH):
    try:
        url = f"{HOSTNAME}/concerto/services/rest/composition/instances/v1/{instance_id}?command=stop"
        response = requests.put(
            url, json={"compositionName": COMPS_PATH}, headers=header, verify=False
        )
        response.raise_for_status()
        print("INFO: Composition is stopped.")
    except Exception as e:
        error_msg = str(response.json()["message"])
        print(
            f"ERROR: An error occurred while stopping the composition {COMPS_PATH}, {error_msg}"
        )


def TerminateGrid(header, HOSTNAME, grid_id, GRID_NAME):
    try:
        url = f"{HOSTNAME}/concerto/services/rest/CloudService/v1/grid/{grid_id}/action"
        response = requests.post(
            url, json={"action": "terminate"}, headers=header, verify=False
        )
        response.raise_for_status()
        print("INFO: Terminating the Grid " + GRID_NAME + "...")
    except Exception as e:
        error_msg = str(response.json()["message"])
        print("INFO: Grid termination failed with error: " + error_msg)
