module "iam" {
  source          = "./baseline-prod/"
  accountId       = "${var.accountId}"
  awsconfigbucket = "${var.awsconfigbucket}"
  providers = {
    aws = "aws.customer_role_frankfurt"
  }
}

module "sns" {
source          = "./securityalert-prod/"
  email = "${var.email}"
  TrailAccountName = "${var.TrailAccountName}"
  providers = {
    aws = "aws.customer_role_nvirginia"
  }
}

