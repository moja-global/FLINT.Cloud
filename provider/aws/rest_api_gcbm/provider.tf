variable "aws_region" {
  default     = "eu-west-1"
  description = "Which region should the resources be deployed into?"
}

provider "aws" {
  region  = "${var.aws_region}"
}
