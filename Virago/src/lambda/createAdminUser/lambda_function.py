import boto3
import secrets
import string
import json
import re
from random import shuffle
iam = boto3.client('iam')
sts = boto3.client('sts')
email = boto3.client('ses',region_name="eu-west-1")
accountId = ""


def createAdminUser(iamclient,username):
        createuserresponse = iamclient.create_user(
        Path='/',
        UserName=username
        )
        attachresponse = iamclient.add_user_to_group(
        GroupName='TSI_Base_Group_PowerUser',
        UserName=username
        )
        upperchars = string.ascii_uppercase 
        lowerchars = string.ascii_lowercase 
        digits = string.digits 
        specchars = "#&@.!"
        password=''.join(secrets.choice(upperchars) for x in range(5))
        password=password+''.join(secrets.choice(lowerchars) for x in range(5))
        password=password+''.join(secrets.choice(digits) for x in range(5))
        password=password+specchars
        password=list(password)
        shuffle(password)
        password=''.join(password)
        profileresponse = iamclient.create_login_profile(
        UserName=username,
        Password=password,
        PasswordResetRequired=True
        )
        return(password)

def createAdminRole(iamclient,rolename,roletrustaccount):
    check = re.compile("^TSI.*",re.IGNORECASE)
    match = check.search(rolename)
    if(match != None):
        raise Exception('Role name must not start with tsi prefix')
    assumerolepolicy = {
    'Version': '2012-10-17',
    'Statement': [
    {
      'Effect': 'Allow',
      'Principal': {
        'AWS': 'arn:aws:iam::{}:root'.format(roletrustaccount)
      },
      'Action': 'sts:AssumeRole',
      'Condition': {}
    }
    ]
    }
    createroleresponse = iamclient.create_role(
    Path='/',
    RoleName=rolename,
    AssumeRolePolicyDocument=json.dumps(assumerolepolicy)
    )
    attachrolesresponse = iamclient.attach_role_policy( RoleName=rolename, PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess')

def sendEmail(iamobject,accountId,emailAddress):
    if(iamobject['roleoruser'] == 'user'):
        logininformation  = """Dear Client,

below is the login information for your new AWS account. You can log in with the username requested as part of the on-boarding process.

URL: https://{}.signin.aws.amazon.com/console
Password: {}

Best regards,
Your T-Managed AWS Team""".format(accountId,iamobject['password'])
    elif(iamobject['roleoruser'] == 'role'):
        logininformation  = """Dear Client,

below is the login information for your new AWS account.

accountid: {}
rolename: {}

Best regards,
Your T-Managed AWS Team""".format(accountId,iamobject['rolename'])

    response = email.send_email(
        Source='service@taws.cloud',
        Destination={
            'ToAddresses': [
                emailAddress ],
            },
        Message={
            'Subject': {
                'Data': 'Login information'
            },
            'Body': {
                'Text': {
                    'Data': logininformation,
                }
            }
        })


def lambda_handler(event, context):
    accountId = str(event['accountId'])
    accountRole='TSI_Base_FullAccess'
    roleArn = 'arn:aws:iam::' + accountId + ':role/' + accountRole
    permissionboundary='arn:aws:iam::' + accountId + ':policy/TSI_Base_PermissionBoundary'
    role = sts.assume_role(RoleArn=roleArn,RoleSessionName='groupcreation')
    iamclient = boto3.client('iam',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])

    if((event['action'] == 'provision') and ('username' in event)):
        password = createAdminUser(iamclient,event['username'])
        iamobject = {}
        iamobject['roleoruser'] = 'user'
        iamobject['password'] = password
        sendEmail(iamobject,event['accountId'],event['email'])
        return(password)
    elif((event['action'] == 'provision') and ('rolename' in event)):

        if('roletrustaccount' in event):
            createAdminRole(iamclient,event['rolename'],event['roletrustaccount'])
            iamobject = {}
            iamobject['roleoruser'] = 'role'
            iamobject['rolename'] = event['rolename']
            sendEmail(iamobject,event['accountId'],event['email'])
        else:
            raise Exception('No roletrustaccount provided')
    else:
        raise Exception('Not valid action or rolename, username not provided')

