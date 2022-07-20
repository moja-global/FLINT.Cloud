# REST API GCBM Terraform integration for Digital Ocean

This Terraform script provisions a Linux App Service which runs the `ghcr.io/moja-global/rest_api_gcbm` Docker container on Digital Ocean.

## Variables

- `do_token` - (Required) This is used to authenticate the Terraform workflow. You can get this token from the Digital Ocean dashboard. Kindly save it, you will need it later. 
- `domain` - (Required) This is the Domain where the app will be hosted. Once added, you can configure this inside the Digital Ocena dashboard.
- `location` - (Required) Email to use Let's Encrypt.

## Outputs

- `docker_compose_config` - Docker compose configuration for Terraform.

## Usage

- Initialize the directory:
  ```sh
  terraform init
  ```

- Deploy the infrastructure:
  ```sh
  terraform apply
  ```
- Destory the infrastructure:
  ```sh
  terraform destory
  ```
  
- Show the infrastructure configuration
  ```sh
  terraform show
  ```

If the plan is acceptable, type "yes" at the confirmation prompt to proceed. Executing the plan will take a few minutes. Once deployed, the Container is launched on the first HTTP Request, which can take a while.
