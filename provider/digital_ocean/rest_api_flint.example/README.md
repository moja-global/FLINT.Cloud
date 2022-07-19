# REST API FLINT.Example Terraform integration for Digital Ocean

This Terraform script provisions a Linux App Service which runs the `ghcr.io/moja-global/rest_api_flint.example` Docker container on Digital Ocean.

## Variables

- `do_token` - (Required) This is used to authenticate the Terraform workflow. You can get this token from Digital Ocean dashboard. 
- `domain` - (Required) This is the Domain where the app will be hosted.
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

If the plan is acceptable, type "yes" at the confirmation prompt to proceed. Executing the plan will take a few minutes. Once deployed, the Container is launched on the first HTTP Request, which can take a while.

## Notes

Continuous Deployment of a single Docker Container can be achieved using the App Setting `DOCKER_ENABLE_CI` to `true`.