# Virago Test

* Author: Stephan.Lo@t-systems.com
* Version: 0.1, 26.09.2018

## Introduction


## install
```bash
# setup local dev
#
# watch your path: export PATH=$PATH:~/.local/bin
virtualenv --python python3 .venv
. .venv/bin/activate
pip install -r requirements.txt -t build
```

## invoke / test local
```bash
#
# switch into sam-environmnet
cd sam
#
# call sam, be sure to have it in your PATH, e.g. 
# export PATH=$PATH:~/.local/bin
#
# generate sample-event
# (alternatively copy sample event from doc/README.txt)
#
sam local generate-event cloudwatch scheduled-event > event.json
#
# invoke 
#
# sync src to build (as incovation runs in build-env)
cp -av ../src/*py ../build/
#
sam local invoke testpolicies -e event.json -d 5678
```

## package

```bash
#
sam package --template-file template.yaml --output-template-file packaged.yaml --s3-bucket 412318185247-pipeline
#
sam deploy --template-file packaged.yaml --stack-name pipeline-testpolicies --capabilities CAPABILITY_IAM
#
aws cloudformation describe-stacks --stack-name pipeline-testpolicies --query 'Stacks[].Outputs'
#
aws  cloudformation describe-stacks --stack-name pipeline-testpolicies
```

## tests with policy-simulator

```bash
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:detach* --resource-arns arn:aws:iam::*:policy/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:detach --resource-arns arn:aws:iam::*:policy/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:groupsa:detach --resource-arns arn:aws:iam::*:policy/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:groupsalkhljhlj:detach --resource-arns arn:aws:iam::*:policy/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:detach --resource-arns arn:aws:iam::*:policy/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam: --resource-arns arn:aws:iam::*:policy/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:groups --resource-arns arn:aws:iam::*:policy/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:user --resource-arns arn:aws:iam::*:policy/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:user --resource-arns arn:aws:iam::*:user/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:user:create --resource-arns arn:aws:iam::*:user/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:create --resource-arns arn:aws:iam::*:user/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:create --resource-arns arn:aws:iam::*:user/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:create --resource-arns arn:aws:iam::*:user/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:delete --resource-arns arn:aws:iam::*:user/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:delete --resource-arns arn:aws:iam::*:user/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:create --resource-arns arn:aws:iam::*:user/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:create --resource-arns arn:aws:iam::*:user/a*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:attach --resource-arns arn:aws:iam::*:user/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:attach --resource-arns arn:aws:iam::*:user/
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:attachuserpolicy --resource-arns arn:aws:iam::*:user/
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:attachuserpolicy --resource-arns arn:aws:iam::*:user/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:attach* --resource-arns arn:aws:iam::*:user/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:Attach* --resource-arns arn:aws:iam::*:user/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:Attach* --resource-arns arn:aws:iam::*:user/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:AttachUserPolicy --resource-arns arn:aws:iam::*:user/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:AttachUserPolicy --resource-arns arn:aws:iam::*:user/*

aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:CreateUser --resource-arns arn:aws:iam::*:user/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:CreateUser --resource-arns arn:aws:iam::*:user/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:Create --resource-arns arn:aws:iam::*:user/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:Create --resource-arns arn:aws:iam::*:user/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:Create --resource-arns arn:aws:iam::*:group/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:CreateGroup --resource-arns arn:aws:iam::*:group/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:T*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:DeleteFunction --resource-arns arn:aws:lambda:*:*:function:T*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:T*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction 
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names iam:CreateGroup --resource-arns arn:aws:iam::*:group/*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:T*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction 
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:TSI_* --context-entries aws:multifactorauthpresent=true
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:TSI_* --context-entries multifactorauthpresent=true
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:TSI_* --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValue=true
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:TSI_* --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:* --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function/* --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda::*:function/* --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:TSI_* --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --resource-arns arn:aws:lambda:*:*:function:TSI_* --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean --resource-arns arn:aws:cloudformation:*:*:stack/StackName-*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean --resource-arns arn:aws:cloudformation:*:*:stack/StackName-*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names lambda:CreateFunction --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean 
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names kms:decrypt --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean --resource-arns arn:aws:cloudformation:*:*:stack/StackName-*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names kms:decrypt --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean 
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names kms:decrypt --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean --resource-arns arn:aws:kms:*:*:alias/TSI_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names kms:decrypt --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean --resource-arns arn:aws:kms:*:*:alias/TSIG_*
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::412318185247:user/A319557 --action-names kms:decrypt --context-entries ContextKeyName=aws:multifactorauthpresent,ContextKeyValues=["true"],ContextKeyType=boolean --resource-arns arn:aws:kms:*:*:alias/TSI_*
```