'''
# ------------------------------------------------------------------------------------------------------------------------
# CT APIs
# ------------------------------------------------------------------------------------------------------------------------
'''
import requests
import json
import Properties
import Authenticate

##############################################
HOSTNAME = Properties.Properties.HOSTNAME
COMPS_PATH = Properties.Properties.COMPS_PATH
GRID_NAME = Properties.Properties.GRID_NAME
##############################################

'''
# Get Grid Id
# Start the Grid
# Check status of the grid
# Load the composition
# Play Loaded Composition
# stop the composition
# Terminate the Grid
'''