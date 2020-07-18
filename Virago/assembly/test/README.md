# Test Stage Artifacts 

`File: assembly/test/README.md`

## Objective
Like in the 'build' stage for the source code deploy the new revision of the test code into an account.

## Stage Actions
Test stage setup has three actions:
1. [README.action-build](action-build/README.md): build source from `test`-code and deploy source into test account
2. [README.action-test](action-test/README.md): run the tests
3. [README.action-cleanup](action-cleanup/README.md): cleanup (not implemented yet)

### Context
AWS Codepipelne supports an information interchange between stages and actions via artifacts.
An example pipeline definition where you can see the handshake-paramrters between the actions is in [test-example-pipline](doc/pipeline-definition.json)

## Stage test
Run the pipeline without commiting to git by uploading the input-artifact of the pipeline into the corresponding s3-bucket:

```bash
cd <virago-root>
PIPELINE_BUCKET=git-to-amazon-s3-outputbucket-1gk8h56mkdvm0
PIPELINE_INPUTARTIFACT=virago_ViragoProject
zip -qr $PIPELINE_INPUTARTIFACT assembly test --exclude=*.venv* --exclude=*/build/* -x $PIPELINE_INPUTARTIFACT -x *_trial* -x */tests/*
aws s3 cp $PIPELINE_INPUTARTIFACT s3://$PIPELINE_BUCKET
rm $PIPELINE_INPUTARTIFACT
```