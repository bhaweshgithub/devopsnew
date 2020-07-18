import boto3
import json
import os

def lambda_handler(event,context):
    cfclient = client = boto3.client('cloudformation')
    accountId = event['accountId'] 
    response = cfclient.update_stack_instances(
    StackSetName='Baseline-{}'.format(os.environ['branchname']),
    Accounts=[
        accountId,
        ],
        Regions=[
        'eu-central-1',
        ],
        ParameterOverrides=
            event['overrides']
        )
    
    return(response)
