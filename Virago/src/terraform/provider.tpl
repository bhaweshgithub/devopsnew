provider "aws" {
  region = "eu-central-1"
  alias  = "customer_role_frankfurt"
  assume_role {
    role_arn     = "arn:aws:iam::${var.accountId}:role/TSI_Base_FullAccess"
    session_name = "terraform"
  }
}

provider "aws" {
  region = "eu-central-1"
  alias  = "customer_role"
  assume_role {
    role_arn     = "arn:aws:iam::${var.accountId}:role/TSI_Base_FullAccess"
    session_name = "terraform"
  }
}
provider "aws" {
  region = "us-east-1"
  alias  = "customer_role_nvirginia"
  assume_role {
    role_arn     = "arn:aws:iam::${var.accountId}:role/TSI_Base_FullAccess"
    session_name = "terraform"
  }
}

terraform {
  backend "s3" {
    bucket = "###terraformbucket###"
    region = "eu-central-1"
  }
}


