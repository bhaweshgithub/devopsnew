#!/bin/bash

if [ $# -ne 6 ]; then
   echo "$0 <ACCOUNT_NO> <ACCOUNT_ALIAS> <CONFIG_BUCKET> <ASUME_ROLE> <DRY_RUN> <CONFIG_ACCOUNT_NO>"
   exit 1
fi

ACCOUNT_NO=$1

ACCOUNT_ALIAS=$2

CONFIG_BUCKET=$3

ASUME_ROLE=$4

DRY_RUN=`echo $5| tr '[:upper:]' '[:lower:]'`

CONFIG_ACCOUNT_NO=$6

nuke_home="/aws-nuke"

echo "Creating aws directory"
mkdir -p ~/.aws

echo "Creating aws config"
echo -e "[default]\nregion = eu-central-1\noutput = json\n\n[profile virasandbox]\nregion = eu-west-1\nrole_arn =arn:aws:iam::${CONFIG_ACCOUNT_NO}:role/${ASUME_ROLE}\ncredential_source=Ec2InstanceMetadata\n\n[profile aws-nuke]\nregion = eu-west-1\nrole_arn =arn:aws:iam::${ACCOUNT_NO}:role/${ASUME_ROLE}\ncredential_source=Ec2InstanceMetadata" > ~/.aws/config

echo "aws config created"
cat ~/.aws/config

echo "Downloading config files from S3: ${CONFIG_BUCKET}"
aws s3 cp s3://${CONFIG_BUCKET}/ ${nuke_home}/ --recursive --profile "virasandbox" || ( echo "Could not download data from s3 bucket: ${CONFIG_BUCKET}"; exit 1 )

echo "Config files downloaded successfuly"
ls -ltr ${nuke_home}/
# check if ACCOUNT_ALIAS exists
#exist_alias=$(aws iam list-account-aliases --profile my-galaxy| grep AccountAliases| awk -F '[' '{ print $2}')

echo "Checking if alias exists: ${ACCOUNT_ALIAS}"
exist_alias=$(aws iam list-account-aliases --profile aws-nuke| tr -d '\n'| tr -s '\t' ' '| awk -F '"' '{ print $4}')

if [ "${exist_alias}" != "${ACCOUNT_ALIAS}" ]; then
    echo "AWS account does not have Alias: ${ACCOUNT_ALIAS}";
    exit 1;
else
    echo "Account alias matches with provided : ${ACCOUNT_ALIAS}"
fi

echo "Updating config with Account number: $ACCOUNT_NO"
sed -i "s/ACCOUNT_NO/$ACCOUNT_NO/g" "${nuke_home}/config.yaml"

current_user=`/usr/bin/id -un`
echo "Current user is: ${current_user}"

if [ ${DRY_RUN} == 'false' ];then
   echo "Running Nuke with DRY_RUN"
   /usr/bin/expect -f /aws-nuke/nukebot-nodryrun "aws-nuke" ${ACCOUNT_ALIAS} > /tmp/${ACCOUNT_ALIAS}.log
   #echo -e "$ACCOUNT_ALIAS\n$ACCOUNT_ALIAS\n" | /go/bin/aws-nuke -c /aws-nuke/config.yaml --verbose --profile "aws-nuke"
else
   echo "Running Nuke without DRY_RUN"
   /usr/bin/expect -f /aws-nuke/nukebot-dryrun "aws-nuke" ${ACCOUNT_ALIAS} > /tmp/${ACCOUNT_ALIAS}.log
   #echo -e "$ACCOUNT_ALIAS\n$ACCOUNT_ALIAS\n" | /go/bin/aws-nuke -c /aws-nuke/config.yaml --verbose --profile "aws-nuke" --no-dry-run
fi