#resource "aws_iam_role_policy_attachment" "automationrole-attach-s3" {
#  role       = "${aws_iam_role.automationrole.name}"
#  policy_arn = "${aws_iam_policy.TSI_Base_S3_DPC_SecDevOps_Policy.arn}"
#}
#resource "aws_iam_role_policy_attachment" "automationrole-attach-vpc" {
#  role       = "${aws_iam_role.automationrole.name}"
#  policy_arn = "${aws_iam_policy.TSI_Base_VPC_Flowlog.arn}"
#}
#resource "aws_iam_role_policy_attachment" "eventbusrole-attach-policy" {
#  role       = "${aws_iam_role.cloudwatcheventrole.name}"
#  policy_arn = "${aws_iam_policy.TSI_Base_EventBus_Policy.arn}"
#}
resource "aws_iam_role_policy_attachment" "configrole-attach-policy-custom" {
  role       = "${aws_iam_role.ConfigRecorderRole.name}"
  policy_arn = "${aws_iam_policy.TSI_Base_CrossAccountBucketPolicy.arn}"
}
resource "aws_iam_role_policy_attachment" "configrole-attach-policy-awsconfigrole" {
  role       = "${aws_iam_role.ConfigRecorderRole.name}"
  policy_arn = "${data.aws_iam_policy.AWSConfigRole.arn}"
}

#resource "aws_iam_role_policy_attachment" "s3dpcrole-attach-policy" {
#  role       = "${aws_iam_role.TSI_Base_S3_DPC_SecDevOps_Role.name}"
#  policy_arn = "${aws_iam_policy.TSI_Base_S3_DPC_SecDevOps_Policy.arn}"
#}

resource "aws_iam_role_policy_attachment" "secondlevelrole-attach-policy" {
  role       = "${aws_iam_role.TSI_Base_2ndLevel_Role.name}"
  policy_arn = "${data.aws_iam_policy.SupportUser.arn}"
}

resource "aws_iam_role_policy_attachment" "tsibackoffice-attach-policy" {
  role       = "${aws_iam_role.TSI_Base_BackOffice_Role.name}"
  policy_arn = "${data.aws_iam_policy.AWSSupportAccess.arn}"
}
resource "aws_iam_role_policy_attachment" "pacbotro-attach-policy-awssupport" {
  role       = "${aws_iam_role.TSI_Base_pacbot_ro.name}"
  policy_arn = "${data.aws_iam_policy.AWSSupportAccess.arn}"
}
resource "aws_iam_role_policy_attachment" "pacbotro-attach-policy-readonly" {
  role       = "${aws_iam_role.TSI_Base_pacbot_ro.name}"
  policy_arn = "${data.aws_iam_policy.ReadOnlyAccess.arn}"
}

resource "aws_iam_role_policy_attachment" "readonlyswitchrole-attach-policy-readonly" {
  role       = "${aws_iam_role.TSI_Base_ReadOnlySwitchRole.name}"
  policy_arn = "${data.aws_iam_policy.ReadOnlyAccess.arn}"
}

resource "aws_iam_role_policy_attachment" "pacbotro-attach-policy-guarddutyreadonly" {
  role       = "${aws_iam_role.TSI_Base_pacbot_ro.name}"
  policy_arn = "${data.aws_iam_policy.AmazonGuardDutyReadOnlyAccess.arn}"
}






resource "aws_iam_group_policy_attachment" "tsibasegrouppoweruser_administratoraccess" {
  group      = "${aws_iam_group.TSI_Base_Group_PowerUser.name}"
  policy_arn = "${data.aws_iam_policy.AdministratorAccess.arn}"
}

resource "aws_iam_group_policy_attachment" "tsibasegrouppoweruser_mfapolicy" {
  group      = "${aws_iam_group.TSI_Base_Group_PowerUser.name}"
  policy_arn = "${aws_iam_policy.TSI_Base_Policy_MFA.arn}"
}




