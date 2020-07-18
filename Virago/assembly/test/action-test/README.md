# Test Stage Artifacts  - Action Test

## Folder structure
* src\
  the code of the action
* build\
  the build artifact to deploy onto the account
* sam\
  the sam template to deploy the code as cloudformation stackset
* requirements.txt\
  python libriaries
* env.test\
  
## Setup
1. deploy the action-test handler lambda function. see `package and deploy` in this file
2. setup manually a 'test stage - test action' in the pipeline, e.g. as declaratively described in [test-action](doc/sample-codepipeline.json) (see ```"name": "TeststageTest"```)
3. choose the lambda `codepipeline-${Branch}-teststage-test` as action


## Example code

https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-invoke-lambda-function.html#actions-invoke-lambda-function-samples-python-cloudformation

## Invoking asynchroneously

* https://blog.symphonia.io/learning-lambda-part-6-dea1740f6c6f
* https://hackernoon.com/how-to-control-asynchronous-invocations-of-your-aws-lambda-functions-ad2def033222
* https://www.concurrencylabs.com/blog/how-to-operate-aws-lambda/
* https://read.acloud.guru/some-lessons-learned-about-lambda-orchestration-1a8b72a33fd2
* https://speakerdeck.com/jboner/how-events-are-reshaping-modern-systems


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
# call sam (be sure to have it in your PATH, e.g. 
# export PATH=$PATH:~/.local/bin)
#
# invoke 
#
# sync src to build (as incovation runs in build-env)
cp -av ../src/*py ../build/
#
sam local invoke -t teststage-test.yaml teststagetestjob -e pipeline-event.json -d 5678
```

## package & deploy

```bash
#
sam package --template-file teststage-test.yaml --output-template-file teststage-test-packaged.yaml --s3-bucket 297193019640-pipeline
#
sam deploy --template-file teststage-test-packaged.yaml --stack-name codepipeline-develop-teststage-test --capabilities CAPABILITY_IAM
#
aws cloudformation describe-stacks --stack-name codepipeline-develop-teststage-test --query 'Stacks[].Outputs'
#
aws  cloudformation describe-stacks --stack-name codepipeline-develop-teststage-test
```

## debugging

### outline
* start runtime on server, export port, wait with 'ptvsd.wait_for_attach()'
* start debugger locally, connect to server
* (this is the over way round as XDebug does where the runtime connects to the debugger)

* Lambda-Debugging: https://docs.aws.amazon.com/lambda/latest/dg/test-sam-cli.html
* VSCode: https://code.visualstudio.com/docs/python/debugging
* VSCode/Python: https://code.visualstudio.com/docs/python/python-tutorial

```
{
    "name": "Python: Attach",
    "type": "python",
    "request": "attach",
    "port": 5300,
    "host": "127.0.0.1",
    "pathMappings": [
        {
            // "localRoot": "${workspaceFolder}",  // You may also manually specify the directory containing your source code.
            "localRoot": "/home/stl/git/ViragoProject/assembly/tests/action-test/src",
            "remoteRoot": "/var/task" // Linux example; adjust as necessary for your OS and situation.
        }
    ],
}
```
```
(.venv) stl@amplatz ~/git/ViragoProject/assembly/pipeline/3_Test_Stage/sam-app  (81-cicd-pipeline) $ sam local invoke HelloWorldFunction -e codepipeline_event.json -d 5300 
```
```
import ptvsd

# Allow other computers to attach to ptvsd at this IP address and port.
ptvsd.enable_attach(address=('0.0.0.0', 5300), redirect_output=True)

# Pause the program until a remote debugger is attached
ptvsd.wait_for_attach()