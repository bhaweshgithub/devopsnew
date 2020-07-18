import boto3

organizations = boto3.client('organizations')

def lambda_handler(event, context):
    if 'customermasteraccountid' in event:
        #Here we need to sts to different master
        stsclient = boto3.client('sts')
        accountRole='TSI_Base_FullAccess'
        roleArn = 'arn:aws:iam::' + event['customermasteraccountid'] + ':role/' + accountRole
        role = stsclient.assume_role(RoleArn=roleArn,RoleSessionName='accountcreation')
        organizations = boto3.client('organizations',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        status = organizations.describe_create_account_status(
        CreateAccountRequestId=event['accountcreate']['CreateAccountStatus']['Id']
        )
    else:
        organizations = boto3.client('organizations')
        status = organizations.describe_create_account_status(
        CreateAccountRequestId=event['accountcreate']['CreateAccountStatus']['Id']
        )
    response = {}
    response['CreateAccountStatus']={}
    response['CreateAccountStatus']['State']=status['CreateAccountStatus']['State']
    response['CreateAccountStatus']['Id']=status['CreateAccountStatus']['Id']
    if(response['CreateAccountStatus']['State']=='FAILED'):
        response['CreateAccountStatus']['FailureReason']=status['CreateAccountStatus']['FailureReason']
    if(status['CreateAccountStatus']['State']=='SUCCEEDED'):
        response['CreateAccountStatus']['AccountId']=status['CreateAccountStatus']['AccountId']
    return(response)

