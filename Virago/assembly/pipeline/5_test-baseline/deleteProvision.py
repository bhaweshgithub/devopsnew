import json
import boto3
import traceback
import sys
import os

payload = {
  "action" : "destroy",
  "accountemail": "gabor.hasenfrasz@t-systems",
  "accountId": "787043465971",
  "email": "gabor.hasenfrasz@t-systems.com",
  "ouname" : "testroot,gabor",
  "username": "A11336167",
  "description": "baseline",
  "accountemail" : "aws-baseline@t-systems.com",
  "terraformversion" : "BaselineV2",
  "terraformbucket" : "a11336167-confidential"
  }


def lambda_handler(event, context):
  code_pipeline = boto3.client('codepipeline')
  try:
    print("EVENT DATA:\n")
    print(event)
    print("-------------\n")
    job_id = event['CodePipeline.job']['id']
    job_data = event['CodePipeline.job']['data']
    print("JOB DATA:")
    print(job_data)
    params = json.loads(job_data['actionConfiguration']['configuration']['UserParameters'])
    sts = boto3.client('sts')
    branchname = params['branchname']
    accountRole='TSI_Base_FullAccess'
    roleArn = 'arn:aws:iam::' + "787043465971" + ':role/' + accountRole
    role = sts.assume_role(RoleArn=roleArn,RoleSessionName='groupcreation')
    iam = boto3.client('iam',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    code_pipeline = boto3.client('codepipeline')
    lambdaclient = boto3.client('lambda')
    sfn = boto3.client('stepfunctions')
    cf = boto3.client('cloudformation')
    if 'continuationToken' in job_data:
      print("ContinuationToken received")
      print(job_data['continuationToken'])
      conttoken = json.loads(job_data['continuationToken'])
      execArn = conttoken['executionArn']
      sfnstatus = sfn.describe_execution(executionArn=execArn)
      if (sfnstatus['status'] == 'SUCCEEDED'):
        print("Status succeeded")
        cf.delete_stack(StackName='provision-{}'.format(os.environ['branchname']))
        cf.delete_stack(StackName='testframework-{}'.format(os.environ['branchname']))
        code_pipeline.put_job_success_result(jobId=job_id)
        return "Complete."
      elif (sfnstatus['status'] == 'RUNNING'):
        print("Status is running")
        continuation_token = json.dumps({'executionArn': execArn})
        code_pipeline.put_job_success_result(jobId=job_id, continuationToken=continuation_token)
      else:
        code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={'type': 'JobFailed', 'message' : 'Failed'})
    else:
        roleslist = ["EC2_TSI_Role","policytestfullRole","policytestuser"]
        for role in roleslist:
            try:
                attachedrolepolicies = iam.list_attached_role_policies( RoleName=role)
                for attachedpolicy in attachedrolepolicies['AttachedPolicies']:
                    iam.detach_role_policy(RoleName=role,PolicyArn=attachedpolicy['PolicyArn'])
                inlinepols = iam.list_role_policies(RoleName=role)
                for inlinepolicyname in inlinepols['PolicyNames']:
                    print(inlinepolicyname)
                    print(iam.delete_role_policy(RoleName=role,PolicyName=inlinepolicyname))
                for instanceprofile in iam.list_instance_profiles_for_role(RoleName=role)['InstanceProfiles']:
                    print(instanceprofile['InstanceProfileName'])
                    iam.remove_role_from_instance_profile(RoleName=role,InstanceProfileName=instanceprofile['InstanceProfileName'])
                    iam.delete_instance_profile(InstanceProfileName=instanceprofile['InstanceProfileName'])

                iam.delete_role(RoleName=role)
            except:
                print("Skipping {}".format(role))
                print(sys.exc_info()[0])
                print(sys.exc_info()[1])
        #delete users
        users = iam.list_users()
        for user in users['Users']:
          for group in iam.list_groups_for_user(UserName=user['UserName'])['Groups']:
            iam.remove_user_from_group(GroupName=group['GroupName'],UserName=user['UserName'])
          try:
              iam.delete_login_profile(UserName=user['UserName'])
          except:
              print("profile already deleted")
          print(user['UserName'])
          iam.delete_user(UserName=user['UserName'])


        sfninput = payload
        response = sfn.start_execution(stateMachineArn="arn:aws:states:eu-central-1:{}:stateMachine:removeProvision-{}".format(os.environ['accountid'],os.environ['branchname']),
                                input=json.dumps(sfninput))
        continuation_token = json.dumps({'executionArn': response['executionArn']})
        code_pipeline.put_job_success_result(jobId=job_id, continuationToken=continuation_token)
  except Exception as e:
    print('Function failed due to exception.')
    print(e)
    traceback.print_exc()
    code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={'type': 'JobFailed', 'message' : 'Failed'})



