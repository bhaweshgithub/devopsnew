resource "aws_iam_role" "automationrole" {
  name               = "TSI_Base_Automation"
  assume_role_policy = "${data.aws_iam_policy_document.assumerolepolicy_devsecops.json}"
}

resource "aws_iam_role" "cloudwatcheventrole" {
  name               = "TSI_Base_EventBus_Role"
  assume_role_policy = "${data.aws_iam_policy_document.assumerolepolicy_aws_events_service.json}"
}

resource "aws_iam_role" "ConfigRecorderRole" {
  name               = "TSI_AWS_configRole"
  assume_role_policy = "${data.aws_iam_policy_document.assumerolepolicy_aws_config_service.json}"
}

resource "aws_iam_role" "TSI_Base_S3_DPC_SecDevOps_Role" {
  name               = "TSI_Base_S3_DPC_SecDevOps_Role"
  assume_role_policy = "${data.aws_iam_policy_document.assumerolepolicy_devsecops.json}"
}

resource "aws_iam_role" "TSI_Base_2ndLevel_Role" {
  name               = "TSI_Base_2ndLevel_Role"
  assume_role_policy = "${data.aws_iam_policy_document.assumerolepolicy_viramaster.json}"
}

resource "aws_iam_role" "TSI_Base_BackOffice_Role" {
  name               = "TSI_Base_BackOffice_Role"
  assume_role_policy = "${data.aws_iam_policy_document.assumerolepolicy_viramaster.json}"
}

resource "aws_iam_role" "TSI_Base_ManagedServices" {
  name               = "TSI_Base_ManagedServices"
  assume_role_policy = "${data.aws_iam_policy_document.assumerolepolicy_viramaster.json}"
}

resource "aws_iam_role" "TSI_Base_ReadOnlySwitchRole" {
  name               = "TSI_Base_ReadOnlySwitchRole"
  assume_role_policy = "${data.aws_iam_policy_document.assumerolepolicy_viramaster.json}"
}




resource "aws_iam_role" "TSI_Base_pacbot_ro" {
  name               = "TSI_Base_pacbot_ro"
  assume_role_policy = "${data.aws_iam_policy_document.assumerolepolicy_devsecops.json}"
}






