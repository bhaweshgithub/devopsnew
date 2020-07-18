# Test Stage Artifacts  - Action Build

* The build action creates the test-source artifact.
* This is done via the means which are done manually during development in [test-development](../../../test/README.md).
* The automatization environment is 'Codebuild'

## Setup
1. setup manually a test stage - build action in the pipeline, e.g. as declaratively described in [build-action](doc/sample-codepipeline.json) (see ```"name": "TeststageBuild"```)
2. setup manually a codebuild-project in the action, e.g. as declaratively described in [build-action](doc/sample-codebuild.json). Especially watch the ```"source['buildspec']"``` param!
3. adjust the configuration for your specific pipeline in `env.test`
4. run the pipeline and watch the cloudwatch output. As result you should have got a new lambda like `"codepipeline-${Branch}-teststage-test-policies"`

## buildspec Concept
The flow in the build process is the same as done manually in `test`:
* install pip
* install sam-cli
* source project env
* create virtual env
* install libraries in `build`
* cp source to `build`
* sam package `build`

## interfaces

```
cd ${CODEBUILD_SRC_DIR}/test/action-build
```