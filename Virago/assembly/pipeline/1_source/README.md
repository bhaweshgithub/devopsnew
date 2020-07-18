# Source Stage Setup

`File: assembly/pipeline/1_source/README.md`

Set up the sourcing stage which will integrate or source resp. the pipeline with gitlab.

# WebHook-Integration of DevOpsGitlab Repository `ViragoProject` with an AWS Virago-Account

## Introduction
### Release Notes
* Author: Stephan.Lo@t-systems.com
* Date: 7 September 2018
* Version: 1.0

### Executive Summary
* Procedure: setup a webhook in DevOpsGitlab to a dedicated Virago-'pipeline'-account
* Result: on git-based events within the `ViragoProject`-repo  the repo will be delivered to an AWS bucket as zip-file

### Rationale
* this document is part of the CI/CD-pipeline task in the Virago-project
* the high-level design of the pipeline is to have a Virago-source management within DevOpsGitlab (http://dol.telekom.de) which triggers the pipeline on events
* this deliverable implements the trigger

## Step 1: Setup AWS-Virago endpoint
### 1.1 Launch cloud formation
1. goto https://aws.amazon.com/quickstart/architecture/git-to-s3-using-webhooks
2. open 'View deployment guide for details'
3. click on 'Launch Quick Start' to enter the cloud formation service
4. log in into the account which will be the provider of the webhook service (which will run the pipeline)

### 1.2 Create stack 'Git-to-Amazon-S3'
1. within the stack templates's paramter setting leave all default values except 'Allowed IPs' which you should set to 0.0.0.0/0 (or a well known IP of the GitLab server)
2. run the stack creation
3. after creation copy the `GitPullWebHookApi`-URL from the outputs

#### Remarks
* the stack creation will not work locally on the commandline as the template is too huge - you must load it into a s3-bucket
* template is here: https://aws-quickstart.s3.amazonaws.com/quickstart-git2s3/templates/git2s3.template


## Step 2: Setup DevOpsGitlab endpoint

### 2.1 Set webhook (i.e. trigger from gitlab to aws)
1. log in into Gitlab (https://dol.telekom.de)
2. open the ViragoProject with `maintainer` permissions
3. in the lefthand navigation go to `Settings -> Integrations`
4. fill in the `GitPullWebHookApi`-URL from above and click 'Add Webhook'
5. click 'Test' and verify that you get 'Hook executed successfully: HTTP 200'

### 2.2 create access token (i.e. authentication from aws to gitlab)
1. in the lefthand navigation go to `Settings -> Repository`
2. click on `Deploy Tokens`
3. create a token and copy the `Username` and `Password`

## Step 3: Patch AWS endpoint's lambda function to do token-based authentication
### Rationale
* the quickstart's lambda function is layed out to do a ssh-key based authentication against GitLab
* in the case of DevOpsGitlab this authentication method is not supported
* thus we created a token in step 2
* we need to patch the endpoint that it authenticates by this Token
* right now the token is hard coded within the source

### 3.1 Patch the source with the token
1. have the ViragoProject repo cloned locally
2. open `assembly/git-to-amazon/vendor/quickstart-git2s3/functions/GitPullS3/lambda_function.py`
3. goto function 'get_userpass' in line 60 and fill in the token-vales from Step 2
4. save the file

### 3.2 deploy new lamda function
1. in folder `assembly/git-to-amazon/vendor/quickstart-git2s3/functions/GitPullS3' create a zip file of the whole content
2. open the AWS console of the target Account
3. open the lambda service page and open 'Git-to-Amazon-S3-GitPullLambda-XXXX' function
4. choose 'upload' and upload and save the zipfile from step 3.1

## Step 4: Test the WebHook
1. in gitlab webhook page press again 'Test'
2. in aws console follow the logs in the cloudwatch log page of the api (like `/aws/lambda/Git-to-Amazon-S3-GitPullLambda-WKHZYW1TIF2N`)
3. Test 1: you should get logs like
```
10:33:48
[2018-09-07 10:33:48,947][INFO] DevOpsGitlab base remote_url: https://dol.telekom.de/gitlab/stlo/gitlabAWS.git
10:33:48
[2018-09-07 10:33:48,947][INFO] DevOpsGitlab clone url: https://gitlab+deploy-token-53:xNSGbN3sJZDUvzFMNrmA@dol.telekom.de/gitlab/stlo/gitlabAWS.git
10:33:48
[2018-09-07 10:33:48,947][INFO] found existing repo, using that...
10:33:48
[2018-09-07 10:33:48,948][INFO] Fetching and merging changes from https://gitlab+deploy-token-53:xNSGbN3sJZDUvzFMNrmA@dol.telekom.de/gitlab/stlo/gitlabAWS.git branch master
10:33:49
[2018-09-07 10:33:49,087][INFO] Creating zipfile...
10:33:49
[2018-09-07 10:33:49,088][INFO] pushing zip to s3://git-to-amazon-s3-outputbucket-1gk8h56mkdvm0/stlo/gitlabAWS/stlo_gitlabAWS.zip
10:33:49
[2018-09-07 10:33:49,288][INFO] Completed S3 upload...
```
4. Test 2: in the output-bucket (like `git-to-amazon-s3-outputbucket-1gk8hxxxxx`) you should get a folder structure `<projectname>/<reponame>/<zipfile>`

## Step 5: Trigger Codepipeline automatically
Follow these instructions:
* https://docs.aws.amazon.com/codepipeline/latest/userguide/create-cloudtrail-S3-source.html

# References
* Binaries: https://github.com/aws-quickstart/quickstart-git2s3/tree/master/functions/packages