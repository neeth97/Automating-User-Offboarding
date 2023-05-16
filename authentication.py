import requests, gcloud_config_helper, google.auth.transport.requests
from utils import *

def get_gcloud_auth_token(config):
    """Authenticate & get the bearer token from google endpoint 
    -----------------------------
    Input params: 
    -----------------------------
    config: dict
    Configuration file with the Application details 

    -----------------------------
    Output params: 
    -----------------------------
    GCLOUD_TOKEN: str
    The authentication token to establish connection with the Teams API 
    """
    GCLOUD_TOKEN = ''
    credentials, project = gcloud_config_helper.default()
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    #check for valid credentials
    if credentials.valid == True:
        GCLOUD_TOKEN = credentials.token
    ## if we're not able to get the token from above process, get the token from the config file
    else:
        GCLOUD_TOKEN = config["GCLOUD_AUTH_KEY"]
    return GCLOUD_TOKEN


def get_mcommunity_auth_token(config,env):
    """Authenticate & get the access token from Mcommunity API for the mentioned environment
    -----------------------------
    Input params: 
    -----------------------------
    config: dictionary
    Configuration file with the Application details 

    env: str
    TEST/PROD environment

    -----------------------------
    Output params: 
    -----------------------------
    access_token: str
    The authentication token to establish connection with the MCommunity API
    """
    if env== "TEST":
        url = config["TEST_MCOMM_AUTH_URL"]
        auth = config["TEST_MCOMM_AUTH_HEADER_AUTH"] 
    elif env == "PROD":
        url = config["PROD_MCOMM_AUTH_URL"]
        auth = config["PROD_MCOMM_AUTH_HEADER_AUTH"]
    payload={}
    headers = {'Authorization': auth,
                'Cookie': config["MCOMM_AUTH_HEADER_COOKIE"]} ##check if this cookie is same for both the environments- Test & Prod
    op = requests.request("POST", url, headers=headers, data=payload)
    access_token = op.json()['access_token']
    return access_token
