
def get_details_aff_changes(mcomm_op_dict,master_aff,teams_df,env):
    """
    Compare the previous, current affiliations files to find the affiliation updates/ changes
    -------------------------------------
    Input Params:
    -------------------------------------
    mcomm_op_dict: dict
    The current affiliations dictionary

    master_aff: dict
    The previous affiliations dictionary

    teams_df: pd.DataFrame
    The pandas Dataframe with the details of the Team including Team id, Team name and the associated member ids, associated development team  

    env: str
    The environment: Test/ Prod for which the affiliation changes are being monitored
    """
   
    ## while processing the affiliations dictionary, for persons with no affiliation - "n/a" is added affiliation
    processed_aff_dict = {k:v['person']['affiliation'] if 'affiliation' in v['person'] else "n/a" for k,v in mcomm_op_dict.items() }

     # New users who don't have affiliations in master_aff file 
    new_users = [k for k in mcomm_op_dict.keys() if k not in master_aff.keys() ]  
    if len(new_users)>0:
        for k in new_users:
            master_aff[k] = ""
        print(f"New users are: {new_users}")

    ## for users, whose affiliation differs with the stored master affiliation, extract them into list
    aff_change_users = [k for k in processed_aff_dict.keys() if processed_aff_dict[k] != master_aff[k]]     
    team_dict = {}
    for mem in aff_change_users:
        team_dict[mem + "_"+env] = teams_df.loc[ teams_df['member_ids'].apply(lambda x: mem in str(x)  ),'team_name' ].to_list() 
    
    if len(aff_change_users) >0:
        aff_change_ls=[]
        for user in aff_change_users:
            aff_change_ls.append( (user, master_aff[user], processed_aff_dict[user], env,team_dict[user+"_"+env]) )
        print("The users with change in affiliations:", aff_change_users)
    else:
        print("The affiliations aren't changed")
    return aff_change_ls, processed_aff_dict
