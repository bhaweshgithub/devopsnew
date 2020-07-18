# Build Stage Setup

`File: assembly/pipeline/2_build/README.md`

Setup the build stage which will build the source artifact (which is the rollout of the baseline product version onto the test account)

* --> should be authored from Gabor as he did the build stage

## Hints / remarks from Stephan

* https://stackoverflow.com/questions/46409771/how-do-you-handle-config-files-for-aws-codepipelines/46410745#46410745
* https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html
* https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html

```
# 1. create new template or get template from existing project
aws codebuild create-project --generate-cli-skeleton > create-project.json
aws codebuild batch-get-projects --names LambdaDeployer | jq .projects[] >> create-project.json
# 2. adjust template
# 3. create new project
aws codebuild create-project --cli-input-json file://create-project.json
```
