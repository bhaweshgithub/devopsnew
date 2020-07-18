import boto3
import json
import os

def lambda_handler(event,context):
    cfclient = client = boto3.client('cloudformation') 
    response = cfclient.create_stack_instances(
    StackSetName='SecurityAlert-{}'.format(os.environ['branchname']),
    Accounts=[
        str(event['accountId']),
    ],
    Regions=[
        "us-east-1",
    ],
    OperationPreferences={
        'FailureTolerancePercentage': 0,
        'MaxConcurrentCount': 1,
    },
    ParameterOverrides=[
        {
            'ParameterKey': 'TrailEmailAddress',
            'ParameterValue': str(event['email'])
        },
        {
            'ParameterKey': 'TrailAccountName',
            'ParameterValue': str(event['description'])
        }
    ]
    )
    
    #return(json.dumps(response))
    return(response)
