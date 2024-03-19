'''
# ------------------------------------------------------------------------------------------------------------------------
# Generate Token
# ------------------------------------------------------------------------------------------------------------------------
'''
import requests
import json
from Properties import Properties

############################################
HOSTNAME = Properties.HOSTNAME
TENANT = Properties.TENANT
USERNAME = Properties.USERNAME
PASSWORD = Properties.PASSWORD
API_TOKEN = Properties.API_TOKEN
############################################

def GetToken(API_TOKEN):
    try:
        url = f"{Properties.HOSTNAME}/concerto/services/rest/RepositoryService/v1/Tokens"
        response = requests.put(url, json={"apiToken": API_TOKEN})
        response.raise_for_status()  # Raises an exception for 4xx and 5xx status codes
        return response.json()['token']
    except requests.RequestException as e:
        print(f"Failed to get token: {e}")
        quit()

def UpdateTenantToken(USERNAME, PASSWORD, TENANT):
    try:
        url = f"{Properties.HOSTNAME}/concerto/services/rest/RepositoryService/v1/Tokens"
        response = requests.put(url, json={"userName":USERNAME, "password":PASSWORD, "tenant":TENANT})
        response.raise_for_status()  # Raises an exception for 4xx and 5xx status codes
        token = response.json()['token']
        print('::::::::::::::Getting Tenant Token::::::::::::::\n'+'INFO: Tenant Auth Token = '+token)
        return token
    except Exception as e:
        print(f"Failed to get Token {e}")
        quit()