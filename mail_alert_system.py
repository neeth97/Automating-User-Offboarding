from SMTPEmail import SMTP
from utils import *


def send_alert(usr_mail,usr_pwd,rec_mail,MSG):
    """
    Send the mail when the sender & recipient mail ids and the body pf the mail is given
    -------------------------------------
    Input Params:
    -------------------------------------
    usr_mail: str
    The username / sender mail id

    usr_pwd: str
    The password of the sender mail id

    rec_mail: str
    The recipient mail id

    MSG: str
    The body of the mail to be mailed to the recipient
    """
    client = SMTP(SMTP_server=  "smtp.mail.umich.edu",#<domain> or <IP_address>,
                SMTP_account= usr_mail,#<account_name>,
                SMTP_password= usr_pwd)#<SMTP_password>
    client.create_mime(recipient_email_addr= rec_mail,sender_email_addr= usr_mail,subject='User Offboarding - Email Alert System',
                    sender_display_name='UMD Capstone Team: Affiliations monitoring',
                    recipient_display_name='ITS Team directory',content_text= MSG)
    client.send_msg()

def group_mails_per_user(mail_alert_ls,TMP_MSG ):
    """
    For the affiliation changes corresponding to multiple environments of a user, collate the mail body to address the affiliation changes for a user from both the environments  
    -------------------------------------
    Input Params:
    -------------------------------------
    mail_alert_ls: list
    The list of affiliation changes where first element in each element is user & the second element being a list of details necessary to draft the affiliation change mail alert

    TMP_MSG: str
    The template body of the mail to be mailed to the recipient for user offboarding purpose

    -------------------------------------
    Output Params:
    -------------------------------------
    mail_alert_dict: dict
    The dictionary with the key being username / uniqname and the value being the mail body to be sent for the affiliation change of the uniqname/ key

    """
    def get_msg(tmplate_msg,user,old_aff,new_aff,env,dev_team):
        """
        Craft a mail body to address the affiliation changes for a user with the given details
        -------------------------------------
        Input Params:
        -------------------------------------
        tmplate_msg: str
        The template body of the mail to be mailed to the recipient for user offboarding purpose

        user: str
        The user for which the affiliation change mail alert is to be crafted 

        old_aff: str
        The old affiliation associated with the given user

        new_aff: str
        The current/ updated affiliation associated with the given user

        env: str
        The environment - Test/ Prod associated with the affiliation change of the given user

        dev_team: str
        The development team the given user is associated with 
        -------------------------------------
        Output Params:
        -------------------------------------
        msg: str
        The mail body encompassing the affiliation changes as per the template shared by API directory team
        """
        msg = tmplate_msg.replace("MEMBER_PLHLDR",str(user) ).replace("OLD_AFF_PLHLDR",str(old_aff) ).replace("NEW_AFF_PLHLDR",str(new_aff))\
            .replace("ENV_PLHLDR",str(env) ).replace("DEV_ORG_PLHLDR",str(dev_team) )
        return msg
    
    mail_alert_dict = {}
    for each_mail in mail_alert_ls:
        ## A user can have affiliation changes in multiple environments,Collecting the affiliation changes for each user - multiple environments -- each_mail[1] = details per env
        # each_mail[0]    -> user
        ### each_mail[1] = each_env_ls => # each_mail[1] -> old_aff ,new_aff,ENV - Test/ Prod, Dev_team

        user, details = each_mail[0], each_mail[1]
        if len(details)>1: ## both environment has affiliation changes
            for each_env_details in details:
                mail_msg = get_msg(TMP_MSG,user,each_env_details[0],each_env_details[1],each_env_details[2],each_env_details[3])
                if user in mail_alert_dict:
                    mail_alert_dict[user]  +=  " \n "+ "\n" + mail_msg
                else:
                    mail_alert_dict[user]  = mail_msg
        else: ## only 1 environment has affiliation changes
            for each_env_details in details:
                mail_msg = get_msg(TMP_MSG,user,each_env_details[0],each_env_details[1],each_env_details[2],each_env_details[3])
                mail_alert_dict[user ] = mail_msg 
    return mail_alert_dict

def send_mails_per_user(config,unique_users,aff_change_ls,TMP_MSG):
    """
    Send the mail for each user affiliation change obtained 
    -------------------------------------
    Input Params:
    -------------------------------------
    config: dict
    Configuration file with the Application details 

    unique_users: list
    The list of distinct uniqnames for whom the affiliations are observed to be changed 

    aff_change_ls: list
    The list of affiliation changes where first element in each element is user & the second element being a list of details necessary to draft the affiliation change mail alert

    TMP_MSG: str
    The template body of the mail to be mailed to the recipient for user offboarding purpose
    """
    mail_alert_ls = [(user,[y[1:] for y in aff_change_ls if y[0]==user]) for user in unique_users]
    print("...CUSTOMIZING MESSAGES FOR EACH USER....") ## Grouping the affiliations change for both Test & Prod by user
    mail_alert_dict = group_mails_per_user(mail_alert_ls,TMP_MSG )

    for user in mail_alert_dict:
        print("Sending mail alert for the change in affiliations observed for user:",user)
        mail_msg = mail_alert_dict[user]
        send_alert(config["SERVICE_USR"], config["SERVICE_PWD"], config["ITS_MAIL"],mail_msg)