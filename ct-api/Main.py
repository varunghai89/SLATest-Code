'''
# ------------------------------------------------------------------------------------------------------------------------
# Description: Automatic Test Execution Using CloudTest API
# Author : Varun Ghai (vghai@akamai.com)
# version: 1.0
# ------------------------------------------------------------------------------------------------------------------------
'''
import os
import requests
import sys
import time
import pandas as pd
import urllib
import urllib3
from Properties import Properties
import Authenticate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

##############################################
ENV_NAME = Properties.ENV_NAME
CTM_TENANT = Properties.CTM_TENANT
HOSTNAME = Properties.HOSTNAME
API_TOKEN = Properties.API_TOKEN
COMPS_PATH = Properties.COMPS_PATH
GRID_NAME = Properties.GRID_NAME
TENANT = Properties.TENANT
USERNAME = Properties.USERNAME
PASSWORD = Properties.PASSWORD
##############################################

# variables
ENV_ID = ''
SLA_ERRORS = 100.0  # in numbers, example: 5.0 is 5%
# Value in seconds, Errors will be checked after 300 seconds
CHECK_ERROR_DURATION = 300
MAX_RETRY_COUNT = 60
MAX_RETRY_DELAY = 30  # Value in Seconds

print('Starting...')
# Generate Token
token = Authenticate.UpdateTenantToken(USERNAME, PASSWORD, TENANT)
header = {"Content-Type": "application/json", "X-Auth-Token": token}

# Get Grid Id
print("INFO: Grid Name = " + GRID_NAME)
url = HOSTNAME + '/concerto/services/rest/RepositoryService/v1/Objects/grid?name=' + GRID_NAME
results = requests.get(url, headers=header, verify=False)
# print(results.text)
print("INFO: Get Grid Id for '" + GRID_NAME + "'")
try:
    # Extract grid_id from the response
    grid_id = str(results.json()['objects'][0]['id'])
    print('INFO: Grid Id: ' + grid_id)

except:
    sys.exit("ERROR: Unable to get the Grid ID!")

time.sleep(10)

# Start the Grid
print("::::::::::::::Starting Grid.::::::::::::::\n" +
      "INFO: Grid Name = " + GRID_NAME + " & Grid Id = " + grid_id)
url = HOSTNAME + '/concerto/services/rest/CloudService/v1/grid/' + grid_id + '/action'
json_str = {"action": "start"}
try:
    results = requests.post(url, json=json_str, headers=header, verify=False)
    # print(results.text)
    print("INFO: Starting the Grid '" + GRID_NAME + "'.")

except:
    sys.exit("ERROR: Unable to start the Grid!")

# Check status of the grid
url = HOSTNAME + '/concerto/services/rest/CloudService/v1/grid/' + grid_id
grid_status_text = ""

for x in range(MAX_RETRY_COUNT):

    try:
        results = requests.get(url, headers=header, verify=False)
        # print(results.text)

        grid_status_text = str(results.json()['state'])
        print("INFO: Grid is " + grid_status_text + "...")

        if grid_status_text == "CHECKED":
            break

    except:
        print('ERROR: Unable to get the status of the Grid!')

        # wait for next status in seconds
    time.sleep(MAX_RETRY_DELAY)

if grid_status_text != "CHECKED":
    sys.exit("ERROR: Please check the status of Grid!")
else:
    print("INFO: 6.  Grid is ready")

time.sleep(10)

# Load the composition
json_str = {"compositionName": COMPS_PATH}
instance_id = None
print("::::::::::::::Loading the Compostition.::::::::::::::\n" +
      "INFO: Composition Name = " + COMPS_PATH)
try:
    results = requests.post(HOSTNAME + '/concerto/services/rest/composition/instances/v1?command=load',
                            json=json_str, headers=header, verify=False)
    instance_id = str(results.json()['instanceID'])
    if instance_id is None:
        sys.exit("ERROR: Load Composition - No Active InstanceID Found!")
    else:
        print("::::::::::::::Compostition is Loaded.::::::::::::::")
except:
    error_msg = str(results.json()['message'])
    if error_msg == 'There are not enough Load Servers available for Tracks in the Composition.':
        print(error_msg + "::::::::::::::Still Playing Composition. ::::::::::::::")
    else:
        sys.exit('ERROR: Load Composition - ' + error_msg + ' ' + COMPS_PATH)

time.sleep(5)


# Play an already loaded Composition
json_str = {"compositionName": COMPS_PATH}
results_id = None
try:
    results = requests.put(HOSTNAME + '/concerto/services/rest/composition/instances/v1/' +
                           instance_id + '?command=play', json=json_str, headers=header, verify=False)
    instance_id = str(results.json()['instanceID'])
    if instance_id is None:
        sys.exit("ERROR: No Active InstanceID Found, Play Composition Failed!")
    else:
        print("::::::::::::::Playing the composition::::::::::::::")
except Exception as e:
    error_msg = str(results.json()['message'])
    sys.exit('ERROR: An error occurred when try to play the composition ' + COMPS_PATH)


# Get Instance Status
PLAY = True
instance_state = None
time.sleep(MAX_RETRY_DELAY)
colHeader = True
while PLAY:
    url = HOSTNAME + '/concerto/services/rest/composition/instances/v1/' + instance_id
    results = requests.get(url, headers=header, verify=False)
    instance_state = str(results.json()['state'])
    print("INFO: Composition " + instance_state + "...")
    if instance_state == "Unloaded":
        break
    results_id = str(results.json()['resultid'])

    # Get duration in seconds
    totalTime = int(results.json()['totalTime'])/1000
    if totalTime > CHECK_ERROR_DURATION:
        # Get clip-element groupBy=error
        url = HOSTNAME + '/concerto/services/rest/Results/v1/' + \
            results_id + '/clip-element?elementType=message'
        results = requests.get(url, headers=header, verify=False)
        # print(results.text)
        totalCount = results.json()['elementTypes'][0]['metrics']['count']
        totalErrors = results.json()['elementTypes'][0]['metrics']['errors']
        errorPercentage = float(totalErrors/totalCount * 100)

        # Check the number of errors aginst the defined SLA
        if errorPercentage > SLA_ERRORS:
            PLAY = False

            # stop the composition
            results_url = HOSTNAME + '/concerto/services/rest/composition/instances/v1/' + \
                instance_id + '?command=stop'
            results = requests.put(
                results_url, json=json_str, headers=header, verify=False)
            url = HOSTNAME + '/concerto/services/rest/Results/v1/' + \
                results_id + '/clip-element?groupBy=error'
            results = requests.get(url, headers=header, verify=False)
            error_Info = str(results.json()['errors'])
            for item in (results.json()['errors']):
                for key, value in item.items():
                    if type(value) is list:
                        if (item['error'] != "No Error"):
                            if colHeader:
                                print("Total Errors: {:.2f}".format(
                                    errorPercentage) + '% which is greater than the defined SLA of ' + str(SLA_ERRORS) + '%')
                                colHeader = False
                            print(item['error'], '->', value[0]
                                  ['metrics']['errors'])

    time.sleep(MAX_RETRY_DELAY)
print('INFO: Composition is stopped.')

time.sleep(5)

# Terminate the Grid
url = HOSTNAME + '/concerto/services/rest/CloudService/v1/grid/' + grid_id + '/action'
json_str = {"action": "terminate"}
try:
    results = requests.post(url, json=json_str, headers=header, verify=False)
    # print(results.text)
    print("INFO: Terminating the Grid " + GRID_NAME + "...")

except:
    sys.exit("ERROR: Unable to Start the Grid!")

print("INFO: Grid is terminated.")

time.sleep(10)

# Pull all results for the composition
header = {"Content-Type": "application/json", "X-Auth-Token": token}
url = HOSTNAME + '/concerto/services/rest/Results/v1?composition=' + \
    urllib.parse.quote(COMPS_PATH)
results = requests.get(url, headers=header, verify=False)
print("::::::::::::::Getting Test Results...::::::::::::::")
latest_result_id = str(results.json()['results'][0]['id'])
print('INFO: Result ID = '+latest_result_id)
exportFileName = str(results.json()['results'][0]['name']) + '.csv'
print('INFO: Filename = '+exportFileName)


# Get Metrics for a resultId
url = HOSTNAME + "/concerto/services/rest/Results/v1/" + latest_result_id + \
    "/collection?percentile=90&percentile=95&percentile=99&groupBy=flattenedHierarchy"
indv_result = requests.get(url, headers=header, verify=False)
final_list = []
for key, value in (indv_result.json().items()):
    for trans in value:
        if (trans['containerType'] == 'transaction'):  # Search for Transaction Container
            ind_trans = trans['metrics']
            trans_name = trans['flattenedHierarchy'].split(
                '/')[-1]  # Get Transaction Name
            trans_count = ind_trans['started']
            trans_min = 'minEffectiveDuration'
            if trans_min in ind_trans:
                trans_min = ind_trans['minEffectiveDuration']
                t_min = format(float(trans_min/1000), ".2f")
            else:
                t_min = 0
            trans_avg = 'effectiveDuration'
            if trans_count <= 0:
                trans_avg = 0
            else:
                if trans_avg in ind_trans:
                    trans_avg = ind_trans['effectiveDuration'] / trans_count
                else:
                    trans_avg = 0
            t_avg = format(float(trans_avg/1000), ".2f")
            trans_max = ind_trans['maxEffectiveDuration']
            t_max = format(float(trans_max/1000), ".2f")
            trans_std = ind_trans['effectiveDurationStandardOfDeviation']
            t_std = format(float(trans_std/1000), ".2f")
            trans_percentiles = ind_trans['percentiles']
            t_percentile_90 = format(
                float(trans_percentiles[0]['value'])/1000, ".2f")
            t_percentile_95 = format(
                float(trans_percentiles[0]['value'])/1000, ".2f")
            t_percentile_99 = format(
                float(trans_percentiles[0]['value'])/1000, ".2f")
            final_list.append([trans_name, trans_count, t_min, t_avg, t_max,
                              t_percentile_90, t_percentile_95, t_percentile_99, t_std])


print(final_list)
df = pd.DataFrame(final_list)
df.rename(columns={0: 'Transaction',
                   1: 'Collections Completed',
                   2: 'Min Duration[s]',
                   3: 'Avg Duration[s]',
                   4: 'Max Duration[s]',
                   5: '90th Percentile[s]',
                   6: '95th Percentile[s]',
                   7: '99th Percentile[s]',
                   8: 'Standard Deviation[s]'}, inplace=True)

# df = df.pivot(index='Transaction')
# Get the current python script path
#
# scriptPath = os.path.abspath(__file__)
script_directory = os.path.dirname(os.path.abspath(__file__))
# path = scriptPath[0:scriptPath.rfind('/')+1]
export_directory = os.path.join(script_directory, "ResultExports")
export_file_path = os.path.join(export_directory, exportFileName)
df.to_csv(export_file_path, index=True, header=True)
# df.to_csv(path + exportFileName, index=True, header=True)
print("INFO: Results Exported to " + export_file_path + exportFileName)

# ------------------------------------------------------------EOF------------------------------------------------------------
