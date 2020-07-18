import json
import boto3
import traceback

payload = {
  "accountemail": "gabor.hasenfrasz@t-systems",
  "accountid": "787043465971",
  "securityemail": "gabor.hasenfrasz@t-systems.com",
  "username": "A11336167",
  "accountname": "baseline",
  "accountcreate": {
    "CreateAccountStatus": {
      "AccountId": "787043465971",
      "State": "SUCCEEDED"
    }
  }
}


def lambda_handler(event, context):
  try:
    print("EVENT DATA:\n")
    print(event)
    print("-------------\n")
    job_id = event['CodePipeline.job']['id']
    job_data = event['CodePipeline.job']['data']
    print("JOB DATA:")
    print(job_data)
    params = json.loads(job_data['actionConfiguration']['configuration']['UserParameters'])
    branchname = params['branchname']
    code_pipeline = boto3.client('codepipeline')
    lambdaclient = boto3.client('lambda')
    sfn = boto3.client('stepfunctions')
    if 'continuationToken' in job_data:
      print("ContinuationToken received")
      print(job_data['continuationToken'])
      conttoken = json.loads(job_data['continuationToken'])
      execArn = conttoken['executionArn']
      sfnstatus = sfn.describe_execution(executionArn=execArn)
      if (sfnstatus['status'] == 'SUCCEEDED'):
        print("Status succeeded")
        code_pipeline.put_job_success_result(jobId=job_id)
        return "Complete."
      elif (sfnstatus['status'] == 'RUNNING'):
        print("Status is running")
        continuation_token = json.dumps({'executionArn': execArn})
        code_pipeline.put_job_success_result(jobId=job_id, continuationToken=continuation_token)
      else:
        code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={'type': 'JobFailed', 'message' : 'Failed'})
    else:
      response = lambdaclient.invoke(FunctionName='deployProvision-{}'.format(branchname),
      Payload=json.dumps(payload)
      )
      returnfromlambda = json.loads(response['Payload'].read())
      continuation_token = json.dumps({'executionArn': returnfromlambda['executionArn']})
      code_pipeline.put_job_success_result(jobId=job_id, continuationToken=continuation_token)
  except Exception as e:
    print('Function failed due to exception.')
    print(e)
    traceback.print_exc()
    put_job_failure(job_id, 'Function exception: ' + str(e))
            