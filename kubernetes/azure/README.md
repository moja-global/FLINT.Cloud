# Kubernetes Deployment for REST API FLINT.Example and REST API GCBM on Azure Kubernetes Services

This setup will help us to create services, deployments and ingress on Azure Kubernetes Services.

## Setup

1. [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) to access azure from command line on local machine.
2. [Login to Azure CLI](https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli).
3. Run following commands to connect cluster:
   ```sh
   az account set --subscription <subscription-id>
   ```

   ```sh
   az aks get-credentials --resource-group flint-kubernetes --name flint-kubernetes
   ```
4. Create a secret using following command for accessing the images from secured Azure Container Registery:
   ```sh
   kubectl create secret docker-registry secret --docker-server=DOCKER_REGISTRY_SERVER --docker-username=DOCKER_USER --docker-password=DOCKER_PASSWORD --docker-email=DOCKER_EMAIL
   ```
   In our case, we have already created the secret using above command so no need to run this command. 
5. Navigate to `kubernetes/azure/reat_api_flint.example` directory and create deployment:
   ```sh
   cd kubernetes/azure/rest_api_flint.example
   kubectl create -f flint-api.yml
   ```
6. Navigate to `kubernetes/azure/reat_api_gcbm` directory and create deployment:
   ```sh
   cd kubernetes/azure/rest_api_gcbm
   kubectl create -f flint-gcbm.yml
   ```
7. Check status using following command:
   ```sh
   kubectl get pods
   ```
   The status should be 'Running'  for the pods we have created. If not we can troubleshoot using follwoing command.
   ```sh
   kubectl describe pod <podname>
   ```
8. If status is 'Running', we can access the service using the <external_ip_address>:8080. The external ip address can be found from `kubectl get pods` command.
