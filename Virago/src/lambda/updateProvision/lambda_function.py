import boto3
import uuid
import json
import os
from boto3 import resource

stepfunctions = boto3.client('stepfunctions')

"""
Pass account id in event which is to be updated: 
{
  "accountid": "787043465971"
}
"""

def lambda_handler(event, context):
    finalresponse={}
    
    accountid = event['accountid']
    entry= get_table_metadata('accounts',accountid)
    
    #print("DB entry: {}".format(entry))

    state = 'SUCCEEDED'
    #accountemail = event['accountemail']
    accountemail = entry['Item']['accountemail']['S']
    accountname = entry['Item']['accountName']['S']
    uuidname = ''.join(accountname.split())
    baselineparms = {}
    baselineparms['accountemail']=accountemail
    baselineparms['accountId'] = accountid
    baselineparms['email']=entry['Item']['securityEmail']['S']
    #baselineparms['action']="update"
    #baselineparms['username']=event['username']
    baselineparms['description']= accountname
    #baselineparms['enabledregions']= entry['Item']['enabledregions']['L']


    parameterOverrides = []
    overrideelement = {}

    overrideelement['ParameterKey'] = 'TrailAccountName'
    overrideelement['ParameterValue'] = accountname
    parameterOverrides.append(overrideelement)

    overrideelement = {}
    overrideelement['ParameterKey'] = 'TrailEmailAddress'
    overrideelement['ParameterValue'] = entry['Item']['securityEmail']['S']
    parameterOverrides.append(overrideelement)

    baselineparms['overrides']=parameterOverrides

    print("baselineparms: {}".format(baselineparms))

    if(state == 'SUCCEEDED' ):
        response = stepfunctions.start_execution(
    stateMachineArn="arn:aws:states:eu-central-1:{}:stateMachine:PROD-Update_Baseline_Release_1-{}".format(os.environ['accountid'],os.environ['branchname']),
    name='{}-{}'.format(uuidname,str(uuid.uuid4())),
    input=json.dumps(baselineparms)
)
        finalresponse = {'executionArn' : response['executionArn']}
    else:
        response = 'FAILED'
    #return(response['executionArn'])
    return(finalresponse)    



def get_table_metadata(table_name,keyVal):
    # The boto3 dynamoDB resource
    Key = { 'accountId': {'S': keyVal}}
    client = boto3.client('dynamodb')
    response = client.get_item( TableName=table_name, Key=Key)
    return response

