# Source Stage Artifacts 

`File: assembly/source/README.md`

Set up the integration or sourcing part resp. within the pipeline from gitlab to aws.

```The code and information here is not usable in a contiguous way.```

Please refer to assemby/pipeline/1_source how to contiguously setup the source stage.
You will come back here when you need to patch the integration lambda-function.

The rest of this file is information which was gathered during the R&D phase.

# POC: Interconnect gitlab or any other external git with AWS-Virago

git2s3 is the middleware to integrate gitlab with aws s3

## Summary
* Use ```git2s3```-quick start template to set up a virago endpoint for git-push-triggers
* setup a test git, connect it to the endpoint and play around with push-events
* reuse this to connent DevOpsLabs-Gitlab with AWS-Virago-baseline CI/CD

* https://github.com/aws-quickstart/quickstart-git2s3/tree/master/functions/packages

## Step 1: Setup AWS-Virago endpoint
* goto https://aws.amazon.com/quickstart/architecture/git-to-s3-using-webhooks/ or https://github.com/aws-quickstart/quickstart-git2s3
* NOTICE: the stack creation will not work locally on the commandline as the template is too huge - you must load it into a s3-bucket
* set allowed IP's to '0.0.0.0/0' (as we currently do not know the gitlab-server IP)
* hint: template is here: https://aws-quickstart.s3.amazonaws.com/quickstart-git2s3/templates/git2s3.template

### Result
```
Stack name:

    Git-to-Amazon-S3

Stack ID:

    arn:aws:cloudformation:eu-central-1:297193019640:stack/Git-to-Amazon-S3/62576a70-8fec-11e8-8e3a-500c52a6ce62
```

## Step 2: connect repo to endpoint
* create a test repo on git side, create and permit a user accessto this repo
* create access via key for this user and copy the ```PublicSSHKey``` into it
* copy the ```GitPullWebHookApi```-URL and add it on the git-side (add webhook typically) (e.g. https://wvjiy5gc19.execute-api.eu-central-1.amazonaws.com/Prod/gitpull)

### Result
* Pushes into the test-git lead to S3-events which pull the git repo and store it into a zip
* e.g. (see directory-structure!) ```https://s3.eu-central-1.amazonaws.com/virago-baseline/stl/baseline/branch/master/stl_baseline_branch_master.zip```
* i.e. branches are covered within folders

## Step 3: [WIP] optional: simulate a pipeline

### create pipeline
* see https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-create.html#pipelines-create-cli
```
aws --region eu-central-1 codepipeline create-pipeline --cli-input-json file://assembly/git-to-amazon/cli-pipeline.json
```

### create cloudwatch event
* see https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-trigger-source-repo-changes-cli.html
* or even better: https://docs.aws.amazon.com/codepipeline/latest/userguide/create-cloudtrail-S3-source-cli.html

* https://docs.aws.amazon.com/codepipeline/latest/userguide/trigger-S3-migration-cwe.html

* https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-s3-bucket-policy-for-cloudtrail.html
```
aws cloudtrail create-trail --name virago-baseline-trail --s3-bucket-name virago-baseline/stl/baseline/branch/master
```

#### bucket Policy and cloudtrial start
* https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-s3-bucket-policy-for-cloudtrail.html#s3-bucket-policy
* https://docs.aws.amazon.com/codepipeline/latest/userguide/create-cloudtrail-S3-source.html
* https://docs.aws.amazon.com/codepipeline/latest/userguide/trigger-S3-migration-cwe.html

* SEE: https://docs.aws.amazon.com/codepipeline/latest/userguide/create-cloudtrail-S3-source-cli.html
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck20150319",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::git-to-amazon-s3-outputbucket-1gk8h56mkdvm0"
        },
        {
            "Sid": "AWSCloudTrailWrite20150319",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::git-to-amazon-s3-outputbucket-1gk8h56mkdvm0/AWSLogs/297193019640/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}

stl@amplatz ~/git/ViragoProject  (81-cicd-pipeline) $ aws cloudtrail create-trail --name gitlabAWS-push --s3-bucket-name git-to-amazon-s3-outputbucket-1gk8h56mkdvm0
{
    "Name": "gitlabAWS-push",
    "S3BucketName": "git-to-amazon-s3-outputbucket-1gk8h56mkdvm0",
    "IncludeGlobalServiceEvents": true,
    "IsMultiRegionTrail": false,
    "TrailARN": "arn:aws:cloudtrail:eu-central-1:297193019640:trail/gitlabAWS-push",
    "LogFileValidationEnabled": false
}

stl@amplatz ~/git/ViragoProject  (81-cicd-pipeline *) $ aws cloudtrail start-logging --name gitlabAWS-push
stl@amplatz ~/git/ViragoProject  (81-cicd-pipeline *) $ aws cloudtrail put-event-selectors --trail-name gitlabAWS-push --event-selectors '[{ "ReadWriteType": "WriteOnly", "IncludeManagementEvents":false, "DataResources": [{ "Type": "AWS::S3::Object", "Values": ["arn:aws:s3:::git-to-amazon-s3-outputbucket-1gk8h56mkdvm0/stlo/gitlabAWS/stlo_gitlabAWS.zip"] }] }]'
{
    "TrailARN": "arn:aws:cloudtrail:eu-central-1:297193019640:trail/gitlabAWS-push",
    "EventSelectors": [
        {
            "ReadWriteType": "WriteOnly",
            "IncludeManagementEvents": false,
            "DataResources": [
                {
                    "Type": "AWS::S3::Object",
                    "Values": [
                        "arn:aws:s3:::git-to-amazon-s3-outputbucket-1gk8h56mkdvm0/stlo/gitlabAWS/stlo_gitlabAWS.zip"
                    ]
                }
            ]
        }
    ]
}

```

#### event
```
stl@amplatz ~/git/ViragoProject  (81-cicd-pipeline *) $ aws iam create-role --role-name git2s3-watch --assume-role-policy-document file://assembly/git-to-amazon/trustpolicyforCWE.json
{
    "Role": {
        "Path": "/",
        "RoleName": "git2s3-watch",
        "RoleId": "AROAJZBYPU7IDPWIK4KK4",
        "Arn": "arn:aws:iam::297193019640:role/git2s3-watch",
        "CreateDate": "2018-09-09T22:59:20Z",
        "AssumeRolePolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "events.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
    }
}

stl@amplatz ~/git/ViragoProject  (81-cicd-pipeline *) $ aws iam put-role-policy --role-name git2s3-watch --policy-name CodePipeline-Permissions-Policy-For-CWE --policy-document file://assembly/git-to-amazon/permissionspolicyforCWE.json

stl@amplatz ~/git/ViragoProject  (81-cicd-pipeline *) $ aws events put-rule --name "MyS3SourceRule" --event-pattern "{\"source\":[\"aws.s3\"],\"detail-type\":[\"AWS API Call via CloudTrail\"],\"detail\":{\"eventSource\":[\"s3.amazonaws.com\"],\"eventName\":[\"PutObject\"],\"resources\":{\"ARN\":[\"arn:aws:s3:::git-to-amazon-s3-outputbucket-1gk8h56mkdvm0/stlo/gitlabAWS/stlo_gitlabAWS.zip\"]}}}"
{
    "RuleArn": "arn:aws:events:eu-central-1:297193019640:rule/MyS3SourceRule"
}

stl@amplatz ~/git/ViragoProject  (81-cicd-pipeline *) $ aws events put-targets --rule MyS3SourceRule --targets Id=1,Arn=arn:aws:codepipeline:eu-central-1:297193019640:CodePipeline-A

An error occurred (ValidationException) when calling the PutTargets operation: RoleArn is required for target arn:aws:codepipeline:eu-central-1:297193019640:CodePipeline-A.

```

### Result
* the pipeline is triggered after pushes

## Running Pipeline

### Source Stage
https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html?icmpid=docs_acp_console#input-output-artifacts

## tbd
* script and automate all that

## Alternative approach
* https://aws.amazon.com/blogs/devops/using-custom-source-actions-in-aws-codepipeline-for-increased-visibility-for-third-party-source-control/
* see CF-template in Launch-Links: https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/new?stackName=CustomSourceActionDemo&templateURL=https://custom-source-action-blog-eu-west-1.s3.amazonaws.com/cloudformation_arch_1.yaml

## References
* Precedent Version: https://aws.amazon.com/blogs/devops/integrating-git-with-aws-codepipeline/
