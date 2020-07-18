import boto3
import uuid
import json
import os

stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    response = stepfunctions.start_execution(
    stateMachineArn="arn:aws:states:eu-central-1:{}:stateMachine:checkRootMFA-{}".format(os.environ['accountid'],os.environ['branchname']),
    name='{}'.format(str(uuid.uuid4())),
    input=json.dumps(event)
)
    finalresponse = {'executionArn' : response['executionArn']}
    return(finalresponse)
