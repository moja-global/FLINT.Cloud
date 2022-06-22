# REST API FLINT.Example Terraform integration for Azure

This Terraform script provisions a Linux App Service which runs the `ghcr.io/moja-global/rest_api_flint.example` Docker container.

## Variables

- `prefix` - (Required) The prefix used for all resources in this example.
- `location` - (Required) Azure Region in which all resources in this example should be provisioned.

## Outputs

- `app_name` - The name of the app.
- `app_url` - The default URL to access the app.

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