variable "domain" {
  description = "The domain where the app will be hosted."
  type        = string
}

variable "email" {
  description = "Email address used when registering certificates with Let's Encrypt."
  type        = string
}

# Set the variable value in *.tfvars file
# or using -var="do_token=..." CLI option
variable "do_token" {}