# Pipeline Artifacts

`File: assembly/pipeline/README.md`

This is the main entry point for setting up the CI/CD.

## Objective

The 'pipeline'-folder contains the artifacts or guidelines to compose the steps in the pipeline itself.
They are deployed into the AWS-Codepipline stages.
This can be done either manually or automaticcaly.
Right now (September 2018) there is no full automatic setup.

## 0_AWSCodePipeline
Set up AWS Codepipline(s) for Virago which are the container elements for the following stages.

## 1_source
Set up the sourcing stage which will integrate or source resp. the pipeline with gitlab.

## 2_build
Setup the build stage which will build the source artifact (which is the rollout of the baseline product version onto the test account)

## 3_test-provisioning
Setup the test-provisioning stage which will deploy the source artifact (which is the deployment of the baseline rules and contents onto the test account)

## 4_test
Setup the test stage which will do functional tests whether the baseline rules are in effect as designed.

## 5_test-baseline
Setup the test-baseline stage which will .... cleanup ???

## 6_prod
Deploy to prod