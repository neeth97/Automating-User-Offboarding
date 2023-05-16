## Files needed: user_offboarding.py,alert_msg_template.txt, master_test_aff_{PREV_DATE}.json, master_prod_aff_{PREV_DATE}.json, config.json/config_test.json
## Needs to be run on system where the gcloud account is authorized and following packages are present:
# SMTPEmail, requests, time, pandas, json, gcloud_config_helper, google.auth.transport.requests

##########################   IMPORTING NECESSARY PACKAGES   ########################


import time

from authentication import *
from utils import *
from data_pull import *
from affiliation_change_monitoring import *
from mail_alert_system import *


def main(config):
    SCRIPT_START_TIME = time.time()
    ##########################   IMPORTING NECESSARY FILES   ########################
    PREV_DATE = config["PREV_DATE"]
    ## Load the local master affiliations for comparison
    master_test_aff, master_prod_aff = read_file(f"master_test_aff_{PREV_DATE}","json"), read_file(f"master_prod_aff_{PREV_DATE}","json")  
    alert_msg_template = read_file("alert_msg_template","txt") ## Load the email alert system message template
    TMP_MSG = ' '.join(alert_msg_template)
    ############################# TEAMS API ####################################
    print("...CALLING TEAMS API TO GET THE TEAMS & ASSOCIATED MEMBERS....")

    GCLOUD_TOKEN = get_gcloud_auth_token(config) ## Use the gcloud auth Token & API end point to call the API
    ## Get the members uniqnames from Teams API
    test_member_uniq_names, test_teams_df = get_processed_teams_df(config,env="TEST",auth_key= GCLOUD_TOKEN)
    prod_member_uniq_names, prod_teams_df = get_processed_teams_df(config,env= "PROD",auth_key= GCLOUD_TOKEN)

    ############################# MCOMMUNITY API ####################################
    ## Get the members - Affiliations for the above members using Mcommunity API
    print("...CALLING MCOMMUNITY API TO GET THE AFFILIATIONS FOR EACH MEMBER....")

    TEST_AUTH_TOKEN, PROD_AUTH_TOKEN  = get_mcommunity_auth_token(config,env="TEST"), get_mcommunity_auth_token(config,env="PROD")
    test_mcomm_op_dict= get_affiliations_for_users_ls(config,test_member_uniq_names,TEST_AUTH_TOKEN,env="TEST") #,sleep_param='first'
    prod_mcomm_op_dict= get_affiliations_for_users_ls(config,prod_member_uniq_names,PROD_AUTH_TOKEN,env="PROD") #,sleep_param='second'

    ############################# MONITOR AFFILIATIONS #################################### 
    print("...PROCESSING API OUTPUTS TO GET THE AFFILIATIONS CHANGES....")

    test_aff_change_ls, test_aff_dict= get_details_aff_changes(test_mcomm_op_dict,master_test_aff,test_teams_df,env="test")
    prod_aff_change_ls, prod_aff_dict= get_details_aff_changes(prod_mcomm_op_dict,master_prod_aff,prod_teams_df,env="prod")
    aff_change_ls = test_aff_change_ls + prod_aff_change_ls ## structure of each element in aff_change_ls: user, old_aff,new_aff,env, dept
    duplicate_users_ls = [each[0] for each in aff_change_ls] ## extract the list of users whose affiliations are changed, which are the first element in the above list
    unique_users = get_unique_from_ls(duplicate_users_ls)  ## extract the list of unique users

    ############################# E-MAIL ALERT SYSTEM #################################### 
    print("Entered the E-MAIL ALERT SYSTEM  code....")
    send_mails_per_user(config,unique_users,aff_change_ls,TMP_MSG) ## TAILOR CUSTOMIZED MESSAGES & MAIL EACH USER 
    ############################# UPDATING THE LOCAL AFFILIATIONS  #################################### 
    timestr = time.strftime("%Y_%m_%d")
    write_file(file=test_aff_dict,file_name="master_test_aff_"+timestr,extension="json")
    write_file(file=prod_aff_dict,file_name="master_prod_aff_"+timestr,extension="json")
    SCRIPT_END_TIME = time.time()
    print("The total time taken to run the script: ",(SCRIPT_END_TIME - SCRIPT_START_TIME) )

if __name__ == "__main__":
    config = read_file("config_test","json")
    # config = read_file("config","json")
    main(config)