resource "aws_iam_role_policy" "TSI_Base_VPC_Flowlog" {
  name   = "TSI_Base_VPC_Flowlog"
  role =  "${aws_iam_role.automationrole.id}"
  policy = "${data.aws_iam_policy_document.TSI_Base_VPC_Flowlog.json}"
}
resource "aws_iam_role_policy" "TSI_Base_EventBus_Policy" {
  name   = "TSI_Base_EventBus_Policy"
  role   = "${aws_iam_role.cloudwatcheventrole.id}"
  policy = "${data.aws_iam_policy_document.TSI_Base_EventBus_Policy.json}"
}
resource "aws_iam_policy" "TSI_Base_CrossAccountBucketPolicy" {
  name   = "TSI_Base_CrossAccountBucketPolicy"
  policy = "${data.aws_iam_policy_document.TSI_Base_CrossAccountBucketPolicy.json}"
}

resource "aws_iam_policy" "TSI_Base_Policy_MFA" {
  name   = "TSI_Base_Policy_MFA"
  description = "${format("Force users with any right access to configure their authentication with MFA before gaining their privileges for  %s", var.accountId)}"
  policy = "${data.aws_iam_policy_document.TSI_Base_Policy_MFA.json}"
}

resource "aws_iam_role_policy" "TSI_Base_S3_DPC_SecDevOps_Policy" {
  name   = "TSI_Base_S3_DPC_SecDevOps_Policy"
  role  = "${aws_iam_role.automationrole.id}" 
  policy = "${data.aws_iam_policy_document.TSI_Base_S3_DPC_SecDevOps_Policy.json}"
}

resource "aws_iam_role_policy" "TSI_Base_S3_DPC_SecDevOps_Policy_inline" {
  name   = "TSI_Base_S3_DPC_SecDevOps_Policy"
  role  = "${aws_iam_role.TSI_Base_S3_DPC_SecDevOps_Role.id}" 
  policy = "${data.aws_iam_policy_document.TSI_Base_S3_DPC_SecDevOps_Policy.json}"
}






data "aws_iam_policy" "AWSConfigRole" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSConfigRole"
}

data "aws_iam_policy" "AdministratorAccess" {
  arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

data "aws_iam_policy" "SupportUser" {
  arn = "arn:aws:iam::aws:policy/job-function/SupportUser"
}
data "aws_iam_policy" "AWSSupportAccess" {
  arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
}
data "aws_iam_policy" "ReadOnlyAccess" {
  arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}
data "aws_iam_policy" "AmazonGuardDutyReadOnlyAccess" {
  arn = "arn:aws:iam::aws:policy/AmazonGuardDutyReadOnlyAccess"
}
