"""
Downloading artifacts for terraform, manages terraform execution with step function
"""

import os
import json
import boto3
import pathlib
from string import Template
import traceback

def downloadTerraformTemplate(version,terraformbucket):
    s3client = boto3.client('s3')
    objectlist = []
    s3resp = s3client.list_objects_v2(Bucket=terraformbucket,Prefix="terraform_templates/{}/".format(version))
    print(s3resp)
    for fileobject in s3resp['Contents']:
        if (fileobject['Size']>0):
            objectlist.append(fileobject['Key'])
            while(('IsTruncated' in s3resp) and (s3resp['IsTruncated'])):
                s3resp = s3client.list_objects_v2(Bucket=terraformbucket,Prefix="terraform_templates/{}/".format(version),ContinuationToken=s3resp['NextContinuationToken'])
                for fileobject in s3resp['Contents']:
                    if (fileobject['Size']>0):
                        objectlist.append(fileobject['Key'])
    print(objectlist)
    for fileobject in objectlist:
        print(fileobject)
        dest = str(pathlib.Path(*pathlib.Path(fileobject).parts[2:]))
        if(os.path.exists(pathlib.Path(dest).parent)):
            s3client.download_file(terraformbucket,fileobject,dest)
        else:
            os.makedirs(pathlib.Path(dest).parent)
            s3client.download_file(terraformbucket,fileobject,dest)





def generateVariableFile():
    #print(taskInput)
    #open('tasktoken','w').write(taskToken)
    variables = {}
    #inputvariable=taskInput
    print("Generating variable file")
    variables['viramaster'] = '275662325630'
    variables['accountId'] = os.environ['accountId']
    variables['email'] = os.environ['email']
    variables['TrailAccountName'] = os.environ['description']
    open('terraform.tfvars.json', 'w').write(json.dumps(variables))

def executeTerraform(accountId,version):
    #raise Exception('Error happened here')
    oscommand = 'terraform init -backend=true -backend-config="key='.format(version)+accountId + '_terraform" >output.log 2>&1'+ ' && terraform apply -auto-approve >>output.log 2>&1'
    executionresp = os.system(oscommand)
    print(executionresp)
    output = {'exitcode' : executionresp, 'output' : open('output.log','r').read()}
    return(output)
    #raise('Error happened here')



if __name__ == '__main__':
    try:
        stsclient = boto3.client('sts')
        sfclient = boto3.client('stepfunctions')
        taskToken = os.environ['taskToken']
        #terraformbucket = os.environ['terraformbucket']
        downloadTerraformTemplate("BaselineV2","a11336167-confidential")
        generateVariableFile()
        terraform_exec = executeTerraform(os.environ['accountId'],"BaselineV2")
        if (terraform_exec['exitcode'] == 0):
            sfclient.send_task_success(taskToken=taskToken,output=json.dumps(terraform_exec))
        else:
            sfclient.send_task_failure(taskToken=taskToken,error="Terraform execution failed", cause=json.dumps(terraform_exec))
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        sfclient = boto3.client('stepfunctions')
        sfclient.send_task_failure(taskToken=taskToken,error=repr(e))

