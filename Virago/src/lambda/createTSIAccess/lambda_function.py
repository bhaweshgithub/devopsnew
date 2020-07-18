import boto3
from time import sleep
from botocore.exceptions import ClientError
import json
import os
iam = boto3.client('iam')
sts = boto3.client('sts')


def lambda_handler(event, context):
    if 'customermasteraccountid' in event:
        #it's external account so need sts two times to create the TSI_Base_FullAccess
        accountRole='TSI_Base_FullAccess'
        roleArn = 'arn:aws:iam::' + event['customermasteraccountid'] + ':role/' + accountRole
        rolecustomermaster = sts.assume_role(RoleArn=roleArn,RoleSessionName='rolereation')
        accountId = event['accountcreate']['CreateAccountStatus']['AccountId']
        stsjump = boto3.client('sts',aws_access_key_id=rolecustomermaster['Credentials']['AccessKeyId'],aws_secret_access_key=rolecustomermaster['Credentials']['SecretAccessKey'], aws_session_token=rolecustomermaster['Credentials']['SessionToken'])
        roleArn = 'arn:aws:iam::' + accountId + ':role/' + 'OrganizationAccountAccessRole'
        rolecustomeraccount = stsjump.assume_role(RoleArn=roleArn,RoleSessionName='rolereation')
        iamclient = boto3.client('iam',aws_access_key_id=rolecustomeraccount['Credentials']['AccessKeyId'],aws_secret_access_key=rolecustomeraccount['Credentials']['SecretAccessKey'], aws_session_token=rolecustomeraccount['Credentials']['SessionToken'])
        awsprincipal = "arn:aws:iam::{}:root".format(os.environ['accountid'])
        assumepolicy = {'Version': '2012-10-17','Statement': [{ 'Effect': 'Allow','Principal': {'AWS': [awsprincipal] },'Action': 'sts:AssumeRole'} ]}
        responserolcreate = iamclient.create_role(
        RoleName='TSI_Base_FullAccess',
        AssumeRolePolicyDocument=json.dumps(assumepolicy)
            )

        for i in range(0,50):
            try:
                responsepolattach = iamclient.attach_role_policy(
                    RoleName=responserolcreate['Role']['RoleName'],
                    PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess'
                    )
            except iamclient.exceptions.NoSuchEntityException as e:
                sleep(5)
                continue
            else:
                break
        return(responsepolattach)
    else:
        print("Nothing needs to be done")
        return("Nothing needs to be done")
