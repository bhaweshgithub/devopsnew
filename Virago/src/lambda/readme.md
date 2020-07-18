### lambda folder

Here the lambda functions should be placed, alongside with the metadata. Every folder must contain the lambda_function.py file (currently only this will be processed)
metadata.json file contains the list of the lambda templates. Every entry should contain a rolename, the source folder name, and optionally environment variables. 

During the procesing accountid, and branchname environment variables automatically added. 

##example:

{
"Lambdas" :
[
        {
                "rolename": "TSI_Base_Lambda_Oss_Provision_Role",
                "source" : "createAccountInOrganizations",
		"environment" : {"name" : "variable"}

        }
]

##lambda functions

#addAccountCWDPCRule
Adds accountid to S3_DPC_Enforce_Baseline cloudwatch rule in all regions.
input needs accountId

#addAccountIDtojson
Adds details for accounts.json file about the provisioned account
input needs accountId, description

#addCloudTrailPolicy
Adds line to bucket policy to allow cloudtrail shipping data to s3 bucket of cloudtrail on the root account
input needs accountId

#addEventBusOnSecDevOps
Adds accountid to the eventbus on all regions inside secdevops account
input needs accountId

#addS3RulesOnCustomerAccount
Adds TSI_Base_CW_Rule_S3_ACL_Send_SecDevops on customer account, in all regions
input needs accountId

#createAccountInOrganizations
Tries to create a new account inside the organizations
input needs accountname,accountemail

#createAdminUser
Creates an admin user in the target account, and sends out email to the customer
input needs accountId, email

#createCloudFormationInstanceBaseline
Creates stackset instance of baseline-PROD on the target account
input needs accountId

#createCloudFormationInstanceSecurityAlert
Creates stackset instance of securityalert on the target account
input needs accountId,email

#createEncryptionKeys
Creates on the target account in every regions 2 keys, one with alias TSI_Base_InternalS3Key, and one with TSI_Base_ConfidentialS3Key
input needs accountId


#createGroup
Creates 10 groups in the target account, with policies attached
input needs accountId

#createPasswordPolicy
Configures password policy on the target account
input needs accountId

#createRole
Creates 10 roles (5 ec2,5 lambda), and attaches policies on them
input needs accountId

#deployProvision
Startes state machine PROD-Provision_Baseline_Release_1
input needs ['accountcreate']['CreateAccountStatus']['AccountId'], event['accountcreate']['CreateAccountStatus']['State'], accountemail,accountname,securityemail,accountid, username,accountname 

#getAccountStatus
Returns the status of the account creation
input needs ['accountcreate']['CreateAccountStatus']['Id'] (carid)

#getStackInstanceStateBaseline
Returns the status of baseline stsack instance
input needs -

#getStackInstanceStateSecurityAlert
Returns the status of the securityalert stack instance
input needs -

#provisionIamAdmin
Creates role for cloudformation on the target account
input needs accountId

#returnFailure
Returns failure

#createSSMRole
Creates ssm role in the target account
