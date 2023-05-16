import requests, time
import pandas as pd
from utils import *


################## TEAMS ############################

def get_teams_json(url,auth_key):
    """
    Provide the API endpoint & Auth token to get the Teams API response json
    -------------------------------------
    Input Params:
    -------------------------------------
    url: str
    The Teams endpoint from which the data can be obtained 
    
    auth_key: str 
    An alphanumeric authentication access key to be provided for accessing the Teams API 

    -------------------------------------
    Output Params:
    -------------------------------------
    response.json() : json
    The Teams API response json with the relevant fields of Team id, Name, and the associated member email ids 
    """

    headers = { 'Authorization': f"Bearer {auth_key}" }
    response = requests.request("GET", url, headers=headers) 
    return response.json()     

## If we get proper API response, process it to get the dataframe with team id, team name, member ids
def process_teams_json(teams):
    """ Extract the relevant fields - Team id, Team Name, email ids of the members to store in a pd.DataFrame
    -------------------------------------
    Input Params:
    -------------------------------------
    teams: dict
    The Teams API response json/ dictionary used to process and get the details of Team id, Name and associate member email ids

    -------------------------------------
    Output Params:
    -------------------------------------
    member_uniq_names: list
    list of uniqnames necessary for the Mcommunity API

    teams_df: pd.DataFrame
    Dataframe with the details of the teams and associated member uniqnames
    """
    if teams['status'] == 'success':
        teams_ls = teams['data']
        teams_ls_proc = []
        for each in teams_ls:
            tmp={}
            tmp['team_id'] = each['id']
            tmp['team_name'] = each['name']
            tmp['member_ids'] =[i['userId'] for i in each['memberships']] ## team_members

            ## Extract the uniqnames from the email ids obtained above ## Example: "abcde@umich.edu" -> "abcde"
            tmp['member_ids'] = [i.replace('@umich.edu','') for i in tmp['member_ids']]
            teams_ls_proc.append(tmp)
        teams_df = pd.DataFrame(teams_ls_proc).reset_index()

        ## The following method is used to obtain the distinct uniqnames from list of lists of uniqnames obtained above
        member_uniq_names= list(set(sum(teams_df['member_ids'].to_list(),[]) ) )
        
    else:
        print(f" Teams API results - status: {teams['status']}")

    return member_uniq_names, teams_df


def get_processed_teams_df(config, env,auth_key):
    """
    Fetch the Teams API response json and process it to extract the relevant details
    -------------------------------------
    Input Params:
    -------------------------------------
    config: dict
    Configuration file with the Application details 
    
    env: str
    The environment corresponding to which the Teams endpoint response is to be obtained 
    
    auth_key: str 
    An alphanumeric authentication access key to be provided for accessing the Teams API 
    
    -------------------------------------
    Output Params:
    -------------------------------------
    member_uniq_names: list
    list of uniqnames necessary for the Mcommunity API

    teams_df: pd.DataFrame
    Dataframe with the details of the teams and associated member uniqnames
    
    """
    if env == "TEST":
        url = config["TEST_TEAMS_API_ENDPOINT"]
    if env == "PROD":
        url = config["PROD_TEAMS_API_ENDPOINT"]

    teams_response = get_teams_json(url,auth_key)
    member_uniq_names,teams_df = process_teams_json(teams_response)
    return member_uniq_names,teams_df


################## MCOMMUNITY ############################

def get_affiliations_for_user(config,uniqname,access_token,env):
    """
    Get the user affiliations for the given username
    -----------------------------------------------
    Input Params:
    -------------------------------------
    config: dict
    Configuration file with the Application details  
    
    uniqname: str 
    A uniqname for the user whose affiliations is to be obtained

    access_token: str
    An alphanumerical token used to establish the connection with the MCommmunity API & obtain the affiliations  
    
    env: str
    The specific environment for which the affiliations are to be obtained for the given user 
    -------------------------------------
    Output Params:
    -------------------------------------
    tmp: dict
    The affiliations dictionary for a given username/ uniqname with additional details
    """
    if env=="TEST":
        url = config["TEST_MCOMM_BASE_URL"]+uniqname
    elif env=="PROD":
        url = config["PROD_MCOMM_BASE_URL"]+uniqname
    # payload={}
    headers = {'Authorization': f"Bearer {access_token}"} 
    response = requests.request("GET", url, headers=headers) 
    tmp = response.json()
    return tmp

## Current API limit for MCommunity API= 200 calls/minute 

def get_affiliations_for_users_ls(config,member_uniq_names,access_token,env):
    """
    Get the user affiliations for the given list of usernames
    -----------------------------------------------
    Input Params:
    -------------------------------------
    config: dict
    Configuration file with the Application details  
    
    member_uniq_names: list 
    A list of uniqnames/ usernames for whom the affiliations are to be obtained

    access_token: str
    An alphanumerical token used to establish the connection with the MCommmunity API & obtain the affiliations  
    
    env: str
    The specific environment for which the affiliations are to be obtained for the given user 
    -------------------------------------
    Output Params:
    -------------------------------------
    mcomm_op_dict: dict
    The affiliations dictionary file with keys as username/ uniqname & the value being associated affiliation
    """
    mcomm_op_dict={}
    AFF_START_TIME = time.time()
    START_TIME = time.time()
    for member in member_uniq_names:
        tmp = get_affiliations_for_user(config,member,access_token,env) 
        if 'errorCode' in tmp:
            if tmp['errorCode'] == 'ERR429':
                print(f"reached ERR429 at index {member_uniq_names.index(member)} and member: {member}")
                elapsed_time = time.time() - START_TIME
                delta_time= (60-elapsed_time) 
                if delta_time<0:
                    delta_time = 20
                    print('elapsed time: ',elapsed_time,'delta time updated to: ',delta_time)
                else:
                    print('elapsed time: ',elapsed_time,'delta time: ',delta_time)
                
                time.sleep(delta_time)
                tmp = get_affiliations_for_user(config,member,access_token,env) 

                while 'errorCode' in tmp:
                    print('waiting 5 for API limit refresh..')
                    time.sleep(5)
                    tmp = get_affiliations_for_user(config,member,access_token,env="TEST") 
                print('API limit got refreshed')    
                START_TIME = time.time()

        mcomm_op_dict[member] = tmp
    AFF_END_TIME = time.time()
    print(f"Time taken for getting affiliations for {len(member_uniq_names)} users : {(AFF_END_TIME - AFF_START_TIME)} seconds")
    return mcomm_op_dict
