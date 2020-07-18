import json
import boto3
import os
from boto3.dynamodb.types import TypeSerializer

def lambda_handler(event, context):
    accountId = str(event['accountId'])
    accountName = str(event['description'])
    accountRole = "customer"
    confidentialKMSKey = 'alias/TSI_Base_ConfidentialS3Key'
    internalKMSKey = 'alias/TSI_Base_InternalS3Key'
    if 'customermasteraccountid' in event:
        masteraccountId = event['customermasteraccountid']
    else:
        masteraccountId = os.environ['accountid']
    readonlyRole = 'TSI_Base_ReadOnlySwitchRole'
    securityEmail = str(event['email'])
    accountemail = str(event['accountemail'])
    enabledregions = event['enabledregions'].split(',')
    supportenabled = 'false'
    awsconfigenabled = 'false'
    if 'config' in event:
        config = event['config']
    else:
        config  = "disabled"
    if 'support' in event:
        support = event['support']
    else:
        config = "disabled"
    ouname = event['ouname']
    terraformVersion = '1.0'
    writeRole = 'TSI_Base_FullAccess'
    featureLevel = 'full'
    dynamoentry={'accountId' : accountId, 'accountName' : accountName, 'config' : config, 'support' : support, 'ouname' : ouname,
                 'accountRole' : accountRole, 'confidentialKMSKey' : confidentialKMSKey, 
                 'internalKMSKey':internalKMSKey, 'masteraccountId':masteraccountId,'readonlyRole' : readonlyRole,
                 'securityEmail' : securityEmail, 'accountemail' : accountemail,'enabledregions': enabledregions, 'supportenabled' : supportenabled, 'awsconfigenabled': awsconfigenabled,
                 'terraformVersion' : terraformVersion, 'writeRole' : writeRole, 'featureLevel' : featureLevel}
    serializer = TypeSerializer()
    print(json.dumps(serializer.serialize(dynamoentry)['M']))
    dynamoclient = boto3.client('dynamodb')
    return(dynamoclient.put_item(TableName='accounts',Item=serializer.serialize(dynamoentry)['M']))
