# Stage Dummy OK Function

Dummy lambda action. Returns 'succeeded'

## install
```bash
# setup local dev
#
# watch your path: export PATH=$PATH:~/.local/bin
virtualenv --python python3 .venv
. .venv/bin/activate
pip install -r requirements.txt -t build
```

### Local development

#### Create dummy event
```bash
cd sam
sam local generate-event codepipeline job > event.json
```

#### local invocation in debug mode
```bash
#
# switch into sam-environmnet
cd sam
#
# call sam (be sure to have it in your PATH, e.g. 
# export PATH=$PATH:~/.local/bin)

# sync src to build (as incovation runs in build-env)
cp -av ../src/*py ../build/

sam local invoke StageDummyOkFunction -e event.json -d 5300
```

## package

```bash
#
sam package --template-file template.yaml --output-template-file dummy-ok-packaged.yaml --s3-bucket 297193019640-pipeline
#
sam deploy --template-file dummy-ok-packaged.yaml --stack-name codepipeline-anybranch-anystage-anyaction-dummyok --capabilities CAPABILITY_IAM
#
aws cloudformation describe-stacks --stack-name codepipeline-anybranch-anystage-anyaction-dummyok --query 'Stacks[].Outputs'
#
aws  cloudformation describe-stacks --stack-name codepipeline-anybranch-anystage-anyaction-dummyok 
```

