import boto3
import uuid
import json
import os

stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    if 'enabledregions' in event:
        regionparam = event['enabledregions']
    else:
        regionparam = 'eu-central-1'
    finalresponse={}
    accountid = event['accountcreate']['CreateAccountStatus']['AccountId']
    state = event['accountcreate']['CreateAccountStatus']['State']
    accountemail =event['accountemail']
    accountname = ''.join(event['accountname'].split())
    uuidname = ''.join(accountname.split())
    baselineparms = {}
    if 'customermasteraccountid' in event:
        baselineparms['customermasteraccountid'] = event['customermasteraccountid']
    if 'config' in event:
        baselineparms['config'] = event['config']
    else:
        baselineparms['config'] = "disabled"
    if 'support' in event:
        baselineparms['support'] = event['support']
    else:
        baselineparms['support'] = "disabled"
    baselineparms['ouname'] = event['ouname']
    baselineparms['accountemail']=event['accountemail']
    baselineparms['accountId'] = accountid
    baselineparms['email']=event['securityemail']
    baselineparms['action']="provision"
    baselineparms['username']=event['username']
    baselineparms['description']=event['accountname']
    baselineparms['enabledregions']=regionparam
    baselineparms['terraformbucket']=os.environ['terraformbucket']
    baselineparms['terraformversion']=os.environ['terraformversion']
    if(state == 'SUCCEEDED' ):
        response = stepfunctions.start_execution(
    stateMachineArn="arn:aws:states:eu-central-1:{}:stateMachine:PROD-Provision_Baseline_Release_1-{}".format(os.environ['accountid'],os.environ['branchname']),
    name='{}-{}'.format(uuidname,str(uuid.uuid4())),
    input=json.dumps(baselineparms)
)
        finalresponse = {'executionArn' : response['executionArn']}
    else:
        response = 'FAILED'
    #return(response['executionArn'])
    return(finalresponse)
