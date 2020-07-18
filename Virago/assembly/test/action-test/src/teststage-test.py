from __future__ import print_function
from boto3.session import Session

import json
import boto3
import tempfile
import botocore
import ptvsd
import traceback
import datetime
import logging
import os
import zipfile

# code from
# https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-invoke-lambda-function.html#actions-invoke-lambda-function-samples-python-cloudformation
#

debugging=int(os.environ.get("debugging", 0))
if debugging == 1:
    # Allow other computers to attach to ptvsd at this IP address and port.
    ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)

    # Pause the program until a remote debugger is attached
    ptvsd.wait_for_attach()

print('Loading function')

cf = boto3.client('cloudformation')
code_pipeline = boto3.client('codepipeline')
lambdafct = boto3.client('lambda')

# configure the payload for the test function,
# the receiver is e.g. test/src/test-policies.py
payload = {
  "account": "", 
  "region": "us-east-1", 
  "detail": {}, 
  "detail-type": "Scheduled Event", 
  "source": "aws.events", 
  "time": "1970-01-01T00:00:00Z", 
  "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c", 
  "resources": [
    "arn:aws:events:us-east-1:123456789012:rule/ExampleRule"
  ],
  "configurationItem": {
    "resourceName": "a",
    "ARN": "arn:aws:iam::297193019640:user/Administrator",
    "resourceType": "AWS::IAM::User",
    "resourceId": "d",
    "awsAccountId": "297193019640",
    "policies": {"POWERFUL_ACTIONS": "0"}
  }
}
  
def put_job_success(job, message):
    """Notify CodePipeline of a successful job
    
    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
        
    Raises:
        Exception: Any exception thrown by .put_job_success_result()
    
    """
    print('Putting job success')
    print(message)
    code_pipeline.put_job_success_result(jobId=job)
  
def put_job_failure(job, message):
    """Notify CodePipeline of a failed job
    
    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
        
    Raises:
        Exception: Any exception thrown by .put_job_failure_result()
    
    """
    print('Putting job failure')
    print(message)
    code_pipeline.put_job_failure_result(jobId=job, failureDetails={'message': message, 'type': 'JobFailed'})
 
def continue_job_later(job, message):
    """Notify CodePipeline of a continuing job
    
    This will cause CodePipeline to invoke the function again with the
    supplied continuation token.
    
    Args:
        job: The JobID
        message: A message to be logged relating to the job status
        continuation_token: The continuation token
        
    Raises:
        Exception: Any exception thrown by .put_job_success_result()
    
    """
    
    # Use the continuation token to keep track of any job execution state
    # This data will be available when a new job is scheduled to continue the current execution
    continuation_token = json.dumps({'previous_job_id': job})
    
    print('Putting job continuation')
    print(message)
    code_pipeline.put_job_success_result(jobId=job, continuationToken=continuation_token)

def start_update_or_create(job_id, stack, template):
    """Starts the stack update or create process
    
    If the stack exists then update, otherwise create.
    
    Args:
        job_id: The ID of the CodePipeline job
        stack: The stack to create or update
        template: The template to create/update the stack with
    
    """
    if stack_exists(stack):
        status = get_stack_status(stack)
        if status not in ['CREATE_COMPLETE', 'ROLLBACK_COMPLETE', 'UPDATE_COMPLETE']:
            # If the CloudFormation stack is not in a state where
            # it can be updated again then fail the job right away.
            put_job_failure(job_id, 'Stack cannot be updated when status is: ' + status)
            return
        
        were_updates = update_stack(stack, template)
        
        if were_updates:
            # If there were updates then continue the job so it can monitor
            # the progress of the update.
            continue_job_later(job_id, 'Stack update started')  
            
        else:
            # If there were no updates then succeed the job immediately 
            put_job_success(job_id, 'There were no stack updates')    
    else:
        # If the stack doesn't already exist then create it instead
        # of updating it.
        create_stack(stack, template)
        # Continue the job so the pipeline will wait for the CloudFormation
        # stack to be created.
        continue_job_later(job_id, 'Stack create started') 

def check_stack_update_status(job_id, stack):
    """Monitor an already-running CloudFormation update/create
    
    Succeeds, fails or continues the job depending on the stack status.
    
    Args:
        job_id: The CodePipeline job ID
        stack: The stack to monitor
    
    """
    status = get_stack_status(stack)
    if status in ['UPDATE_COMPLETE', 'CREATE_COMPLETE']:
        # If the update/create finished successfully then
        # succeed the job and don't continue.
        put_job_success(job_id, 'Stack update complete')
        
    elif status in ['UPDATE_IN_PROGRESS', 'UPDATE_ROLLBACK_IN_PROGRESS', 
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'CREATE_IN_PROGRESS', 
    'ROLLBACK_IN_PROGRESS']:
        # If the job isn't finished yet then continue it
        continue_job_later(job_id, 'Stack update still in progress') 
       
    else:
        # If the Stack is a state which isn't "in progress" or "complete"
        # then the stack update/create has failed so end the job with
        # a failed result.
        put_job_failure(job_id, 'Update failed: ' + status)

def get_user_params(job_data):
    """Decodes the JSON user parameters and validates the required properties.
    
    Args:
        job_data: The job data structure containing the UserParameters string which should be a valid JSON structure
        
    Returns:
        The JSON parameters decoded as a dictionary.
        
    Raises:
        Exception: The JSON can't be decoded or a property is missing.
        
    """
    try:
        # Get the user parameters which contain the stack, artifact and file settings
        user_parameters = job_data['actionConfiguration']['configuration']['UserParameters']

        print(user_parameters)
        #user_parameters = "{\"stack\": \"virago-codepipeline-teststage-testpolicies\",\"artifact\": \"devpipelinetestbuild\",\"file\": \"test/sam/packaged.yaml\"}"
        decoded_parameters = json.loads(user_parameters)
        print(decoded_parameters)
            
    except Exception as e:
        # We're expecting the user parameters to be encoded as JSON
        # so we can pass multiple values. If the JSON can't be decoded
        # then fail the job with a helpful message.
        raise Exception('UserParameters could not be decoded as JSON')
    
    if 'branch' not in decoded_parameters:
        # Validate that the stack is provided, otherwise fail the job
        # with a helpful message.
        raise Exception('Your UserParameters JSON must include the branch name')
    
    #if 'artifact' not in decoded_parameters:
        # Validate that the artifact name is provided, otherwise fail the job
        # with a helpful message.
    #    raise Exception('Your UserParameters JSON must include the artifact name')
    
    #if 'file' not in decoded_parameters:
        # Validate that the template file is provided, otherwise fail the job
        # with a helpful message.
    #    raise Exception('Your UserParameters JSON must include the template file name')
    
    return decoded_parameters
    
def setup_s3_client(job_data):
    """Creates an S3 client
    
    Uses the credentials passed in the event by CodePipeline. These
    credentials can be used to access the artifact bucket.
    
    Args:
        job_data: The job data structure
        
    Returns:
        An S3 client with the appropriate credentials
        
    """
    key_id = job_data['artifactCredentials']['accessKeyId']
    key_secret = job_data['artifactCredentials']['secretAccessKey']
    session_token = job_data['artifactCredentials']['sessionToken']
    
    session = Session(aws_access_key_id=key_id,
        aws_secret_access_key=key_secret,
        aws_session_token=session_token)

    c = session.client('s3', config=botocore.client.Config(signature_version='s3v4'))

    return c

def lambda_handler(event, context):
    """The Lambda function handler
    
    If a continuing job then checks the CloudFormation stack status
    and updates the job accordingly.
    
    If a new job then kick of an update or creation of the target
    CloudFormation stack.
    
    Args:
        event: The event passed by Lambda
        context: The context passed by Lambda
        
    """

    print("STL IN LAMBDA")
    print("EVENT")
    print(event)
    print("CONTEXT")
    print(vars(context))
    print("EOF")

    try:
        # Extract the Job ID
        job_id = event['CodePipeline.job']['id']
        
        # Extract the Job Data 
        job_data = event['CodePipeline.job']['data']
        
        # Extract the params
        params = get_user_params(job_data)
        
        # simple interface for test configuration
        policies = {}
        if 'policies' in params:
           policies = params['policies']
           # pass policies
           payload['configurationItem']['policies'] = policies

        # Get the list of artifacts passed to the function
        artifacts = job_data['inputArtifacts']
        
        # envvar 'branch' was set in the SAM-template
        branch = params['branch']
        testFunctionName = 'codepipeline-' + branch + '-teststage-test-policies'
        payloadLocal = json.dumps(payload)

        response = lambdafct.invoke(FunctionName=testFunctionName, Payload=payloadLocal)
        testresult = json.loads(response['Payload'].read())

        print("TESTRESULT")
        print(testresult)

        if testresult == 'OK':
            put_job_success(job_id, 'All tests passed')
        else:
            put_job_failure(job_id, 'Tests not passed')

    except Exception as e:
        # If any other exceptions which we didn't expect are raised
        # then fail the job and log the exception message.
        print('Function failed due to exception.') 
        print(e)
        traceback.print_exc()
        put_job_failure(job_id, 'Function exception: ' + str(e))
      
    print('Function complete.')   
    return "Complete."
