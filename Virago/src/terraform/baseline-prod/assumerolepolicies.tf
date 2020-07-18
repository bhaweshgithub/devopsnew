data "aws_iam_policy_document" "assumerolepolicy_viramaster" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = ["${format("arn:aws:iam::%s:root", var.viramasteraccountid)}"]
    }
    effect = "Allow"

  }
}

data "aws_iam_policy_document" "assumerolepolicy_devsecops" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = ["${format("arn:aws:iam::%s:root", var.devsecopsaccountid)}"]
    }
    effect = "Allow"

  }
}

data "aws_iam_policy_document" "assumerolepolicy_aws_events_service" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    effect = "Allow"

  }
}

data "aws_iam_policy_document" "assumerolepolicy_aws_config_service" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["config.amazonaws.com"]
    }
    effect = "Allow"

  }
}
