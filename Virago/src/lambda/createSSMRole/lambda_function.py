import boto3
from time import sleep
from botocore.exceptions import ClientError
iam = boto3.client('iam')
sts = boto3.client('sts')
accountId = ""


def lambda_handler(event, context):
    accountId = str(event['accountId'])
    accountRole='TSI_Base_FullAccess'
    roleArn = 'arn:aws:iam::' + accountId + ':role/' + accountRole
    role = sts.assume_role(RoleArn=roleArn,RoleSessionName='rolereation')
    iamclient = boto3.client('iam',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    responserolcreate = iamclient.create_role(
    RoleName='EC2_TSI_Role',
    AssumeRolePolicyDocument="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": ["ec2.amazonaws.com","ssm.amazonaws.com"]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}"""
            )

    iamclient.create_instance_profile(
    InstanceProfileName='EC2_TSI_Role',
    )

    iamclient.add_role_to_instance_profile(
            InstanceProfileName='EC2_TSI_Role',
            RoleName='EC2_TSI_Role'
            )
    for i in range(0,50):
        try:
            responsepolattach = iamclient.attach_role_policy(
                    RoleName=responserolcreate['Role']['RoleName'],
                    PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM'
                    )
            responsepolattach = iamclient.attach_role_policy(
                    RoleName=responserolcreate['Role']['RoleName'],
                    PolicyArn='arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy'
                    )
            responsepolattach = iamclient.attach_role_policy(
                    RoleName=responserolcreate['Role']['RoleName'],
                    PolicyArn='arn:aws:iam::aws:policy/AmazonSSMFullAccess'
                    )
        except iamclient.exceptions.NoSuchEntityException as e:
            sleep(5)
            continue
        else:
            break

