data "aws_iam_policy_document" "s3secdevopspolicy" {
  statement {
    sid    = "VisualEditor0"
    effect = "Allow"
    actions = [
      "s3:ListBucketByTags",
      "s3:GetLifecycleConfiguration",
      "s3:GetBucketTagging",
      "s3:GetInventoryConfiguration",
      "s3:PutAnalyticsConfiguration",
      "s3:PutAccelerateConfiguration",
      "s3:ListBucketVersions",
      "s3:GetBucketLogging",
      "s3:GetAccelerateConfiguration",
      "s3:GetBucketPolicy",
      "s3:PutBucketTagging",
      "s3:GetBucketRequestPayment",
      "s3:PutLifecycleConfiguration",
      "s3:PutBucketAcl",
      "s3:GetMetricsConfiguration",
      "s3:PutBucketVersioning",
      "s3:GetIpConfiguration",
      "s3:PutObjectAcl",
      "s3:ListBucketMultipartUploads",
      "s3:GetBucketWebsite",
      "s3:PutMetricsConfiguration",
      "s3:GetBucketVersioning",
      "s3:PutBucketCORS",
      "s3:GetBucketAcl",
      "s3:GetBucketNotification",
      "s3:PutInventoryConfiguration",
      "s3:ListMultipartUploadParts",
      "s3:PutIpConfiguration",
      "s3:PutBucketNotification",
      "s3:PutBucketWebsite",
      "s3:PutBucketLogging",
      "s3:PutObjectVersionAcl",
      "s3:GetBucketCORS",
      "s3:GetAnalyticsConfiguration",
      "s3:PutBucketPolicy",
      "s3:GetBucketLocation",
      "s3:PutEncryptionConfiguration",
      "s3:GetEncryptionConfiguration"

    ]
    resources = ["arn:aws:s3:::*"]

  }
}

data "aws_iam_policy_document" "TSI_Base_VPC_Flowlog" {
  statement {
    sid    = "VisualEditor0"
    effect = "Allow"
    actions = [
      "ec2:DeleteTags",
      "ec2:CreateTags"

    ]
    resources = ["arn:aws:ec2:*:*:vpc/*"]

  }
  statement {
    sid    = "VisualEditor1"
    effect = "Allow"
    actions = [
      "logs:CreateLogDelivery",
      "ec2:CreateFlowLogs",
      "ec2:DescribeVpcs",
      "ec2:DescribeFlowLogs"

    ]
    resources = ["*"]

  }
}

data "aws_iam_policy_document" "TSI_Base_EventBus_Policy" {
  statement {
    sid    = "VisualEditor0"
    effect = "Allow"
    actions = [
      "events:PutEvents",

    ]
    resources = ["${format("arn:aws:events:*:%s:event-bus/default", var.devsecopsaccountid)}"]

  }
}
data "aws_iam_policy_document" "TSI_Base_CrossAccountBucketPolicy" {
  statement {
    sid    = "VisualEditor0"
    effect = "Allow"
    actions = [
      "s3:PutObject*",

    ]
    resources = ["${format("arn:aws:s3:::%s/%s", var.awsconfigbucket, var.accountId)}"]
    condition {
      test     = "StringLike"
      variable = "s3:x-amz-acl"
      values = [
        "bucket-owner-full-control"
      ]

    }
  }
  statement {
    sid       = "VisualEditor1"
    effect    = "Allow"
    actions   = ["s3:GetBucketAcl"]
    resources = ["${format("arn:aws:s3:::%s", var.awsconfigbucket)}"]
  }

  statement {
    sid       = "VisualEditor2"
    effect    = "Allow"
    actions   = ["sns:*"]
    resources = ["*"]
  }

}

data "aws_iam_policy_document" "TSI_Base_Policy_MFA" {
  statement {
    sid    = "AllowAllUsersToListAccounts"
    effect = "Allow"
    actions = [

      "iam:ListAccountAliases",
      "iam:ListUsers",
      "iam:GetAccountSummary"

    ]
    resources = ["*"]
  }
  statement {
    sid    = "AllowIndividualUserToSeeAndManageOnlyTheirOwnAccountInformation"
    effect = "Allow"
    actions = ["iam:ChangePassword",
      "iam:CreateAccessKey",
      "iam:CreateLoginProfile",
      "iam:DeleteAccessKey",
      "iam:DeleteLoginProfile",
      "iam:GetAccountPasswordPolicy",
      "iam:GetLoginProfile",
      "iam:ListAccessKeys",
      "iam:UpdateAccessKey",
      "iam:UpdateLoginProfile",
      "iam:ListSigningCertificates",
      "iam:DeleteSigningCertificate",
      "iam:UpdateSigningCertificate",
      "iam:UploadSigningCertificate",
      "iam:ListSSHPublicKeys",
      "iam:GetSSHPublicKey",
      "iam:DeleteSSHPublicKey",
      "iam:UpdateSSHPublicKey",
    "iam:UploadSSHPublicKey"]
    resources = ["${format("arn:aws:iam::%s:user/$${aws:username}", var.accountId)}"]
  }

  statement {
    sid    = "AllowIndividualUserToListOnlyTheirOwnMFA"
    effect = "Allow"
    actions = ["iam:ListVirtualMFADevices",
    "iam:ListMFADevices"]
    resources = ["${format("arn:aws:iam::%s:mfa/*", var.accountId)}",
      "${format("arn:aws:iam::%s:user/$${aws:username}", var.accountId)}"

    ]
  }
  statement {
    sid    = "AllowIndividualUserToManageTheirOwnMFA"
    effect = "Allow"
    actions = ["iam:CreateVirtualMFADevice",
      "iam:DeleteVirtualMFADevice",
      "iam:RequestSmsMfaRegistration",
      "iam:FinalizeSmsMfaRegistration",
      "iam:EnableMFADevice",
      "iam:ResyncMFADevice"
    ]
    resources = ["${format("arn:aws:iam::%s:mfa/$${aws:username}", var.accountId)}",
      "${format("arn:aws:iam::%s:user/$${aws:username}", var.accountId)}"

    ]
  }
  statement {
    sid    = "AllowIndividualUserToDeactivateOnlyTheirOwnMFAOnlyWhenUsingMFA"
    effect = "Allow"
    actions = ["iam:DeactivateMFADevice"
    ]
    resources = ["${format("arn:aws:iam::%s:mfa/$${aws:username}", var.accountId)}",
      "${format("arn:aws:iam::%s:user/$${aws:username}", var.accountId)}"

    ]
    condition {
      test     = "Bool"
      variable = "aws:MultiFactorAuthPresent"
      values = [
        false
      ]

    }
  }
  statement {
    sid         = "BlockAnyAccessOtherThanAboveUnlessSignedInWithMFA"
    effect      = "Deny"
    not_actions = ["iam:*"]
    resources   = ["*"]
    condition {
      test     = "BoolIfExists"
      variable = "aws:MultiFactorAuthPresent"
      values = [
        false
      ]

    }
  }

}

data "aws_iam_policy_document" "TSI_Base_S3_DPC_SecDevOps_Policy" {
  statement {
    sid    = "VisualEditor0"
    effect = "Allow"
    actions = [
      "s3:ListBucketByTags",
      "s3:GetLifecycleConfiguration",
      "s3:GetBucketTagging",
      "s3:GetInventoryConfiguration",
      "s3:PutAnalyticsConfiguration",
      "s3:PutAccelerateConfiguration",
      "s3:ListBucketVersions",
      "s3:GetBucketLogging",
      "s3:GetAccelerateConfiguration",
      "s3:GetBucketPolicy",
      "s3:PutBucketTagging",
      "s3:GetBucketRequestPayment",
      "s3:PutLifecycleConfiguration",
      "s3:PutBucketAcl",
      "s3:GetMetricsConfiguration",
      "s3:PutBucketVersioning",
      "s3:GetIpConfiguration",
      "s3:PutObjectAcl",
      "s3:ListBucketMultipartUploads",
      "s3:GetBucketWebsite",
      "s3:PutMetricsConfiguration",
      "s3:GetBucketVersioning",
      "s3:PutBucketCORS",
      "s3:GetBucketAcl",
      "s3:GetBucketNotification",
      "s3:PutInventoryConfiguration",
      "s3:ListMultipartUploadParts",
      "s3:PutIpConfiguration",
      "s3:PutBucketNotification",
      "s3:PutBucketWebsite",
      "s3:PutBucketLogging",
      "s3:PutObjectVersionAcl",
      "s3:GetBucketCORS",
      "s3:GetAnalyticsConfiguration",
      "s3:PutBucketPolicy",
      "s3:GetBucketLocation",
      "s3:PutEncryptionConfiguration",
      "s3:GetEncryptionConfiguration"

    ]
    resources = ["arn:aws:s3:::*"]

  }
}


