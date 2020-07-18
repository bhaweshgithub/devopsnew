from __future__ import print_function
from boto3.session import Session

import json
import boto3
import tempfile
import botocore
import ptvsd
import traceback

# Allow other computers to attach to ptvsd at this IP address and port.
#ptvsd.enable_attach(address=('0.0.0.0', 5300), redirect_output=True)
# Pause the program until a remote debugger is attached
#ptvsd.wait_for_attach()

print('Loading function')

cf = boto3.client('cloudformation')
code_pipeline = boto3.client('codepipeline')


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


def find_artifact(artifacts, name):
    """Finds the artifact 'name' among the 'artifacts'

    Args:
        artifacts: The list of artifacts available to the function
        name: The artifact we wish to use
    Returns:
        The artifact dictionary found
    Raises:
        Exception: If no matching artifact is found

    """
    print('Artifacts:')
    for artifact in artifacts:
        print (artifact['name'])
        print (artifact['location']['type'])
        print (artifact['location']['s3Location']['bucketName'])
        print (artifact['location']['s3Location']['objectKey'])
        # if artifact['name'] == name:
        #    return artifact

    # raise Exception('Input artifact named "{0}" not found in event'.format(name))


def check_job_update_status(job_id):
    """Monitor an already-running Job update/create

    Succeeds, fails or continues the job depending on the stack status.

    Args:
        job_id: The CodePipeline job ID
        ...: specific stuff

    """
    status = 0
    if status in [1, 2]:
        # If the update/create finished successfully then
        # succeed the job and don't continue.
        put_job_success(job_id, 'Job complete')

    elif status in [3, 4, 5]:
        # If the job isn't finished yet then continue it
        continue_job_later(job_id, 'Job still in progress')

    else:
        # If the Stack is a state which isn't "in progress" or "complete"
        # then the stack update/create has failed so end the job with
        # a failed result.
        put_job_failure(job_id, 'Job failed: ' + status)


def lambda_handler(event, context):

    try:
        # Extract the Job ID
        job_id = event['CodePipeline.job']['id']
        print('Job id is %s' % job_id)

        # Extract the Job Data
        job_data = event['CodePipeline.job']['data']

        # Get the list of artifacts passed to the function
        artifacts = job_data['inputArtifacts']

        find_artifact(artifacts, 'no name')

        if 'continuationToken' in job_data:
            # If we're continuing then the create/update has already been triggered
            # we just need to check if it has finished.

            check_job_update_status(job_id)
        else:
            response = code_pipeline.get_job_details(jobId=job_id)

            put_job_success(job_id, 'Dummy function worked.')

    except Exception as e:
        # If any other exceptions which we didn't expect are raised
        # then fail the job and log the exception message.
        print('Function failed due to exception.')
        print(e)
        traceback.print_exc()
        put_job_failure(job_id, 'Function exception: ' + str(e))

    print('Function complete.')
    return "Complete."
