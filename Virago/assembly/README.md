# Assembly Code

`File: assembly/README.md`

This directory contains information and deployment code to setup a pipeline in an account.

## pipeline
The AWS Codepipeline itself

## source
The source stage of the pipeline.
Set up the integration or sourcing part resp. from gitlab to aws.

## build
The build stage of the pipeline.
Deploy the new revision of the product into an account.

Hint:
Carefully distinguish between 'build' as action and 'build' as stage.
E.g. in 'buildspec.build.yml' the first build is the action, whereas the latter is the stage.
That's why in 'buildspec.prod.yml' the product is built for the prod stage.

## test-provisioning
The test-provisioning stage of the pipeline.
'Run' the new product revision such that it is testable.

## test
The test stage of the pipeline.
Same as in the build stage deploy the new revision of the test code into an account.

## test-baseline
The test-baseline stage of the pipeline.
Cleanup the test account.

## prod
The prod stage of the pipeline.
Deploy the new revision of the product into production.