import boto3
import json
import os

def lambda_handler(event,context):
    cfclient = client = boto3.client('cloudformation') 
    response = cfclient.create_stack_instances(
    StackSetName='Baseline-{}'.format(os.environ['branchname']),
    Accounts=[
        str(event['accountId']),
    ],
    Regions=[
        "eu-central-1",
    ],
    OperationPreferences={
        'FailureTolerancePercentage': 0,
        'MaxConcurrentCount': 1,
    },
    ParameterOverrides=[{'ParameterKey': 'enabledregions', 'ParameterValue' : str(event['enabledregions'])}]
    )
    
    return(response)
