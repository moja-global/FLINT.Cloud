.. _Deployment:

FLINT.Cloud Deployment
####################

This section guides you through the process of deploying FLINT.Cloud to
your own server, through a public cloud service provider. We use
Google Cloud Platform (GCP) and Azure to deploy FLINT.Cloud
APIs that are used by FLINT-specific applications, like FLINT-UI.
This guide assumes that you have some knowledge of the
concepts of GCP and Azure, and that you have successfully deployed an application before.

Google Cloud Platform
---------------------

To deploy FLINT.Cloud to GCP, we provide a
production grade setup using a Layered Architecture setup on top of the
Google Cloud. In this setup we use `Terraform`_, an
Infrastructure-as-a-Code tool, to deploy the infrastructure and the
applications we want to use.

To deploy the FLINT.Cloud to GCP, follow these steps:

1. Create a GCP service account with project owner permissions in your
   project. This is used by Terraform to provision all the necessary
   resources.
2. Copy ``main.tf`` from the ``layered`` directory of this repository to
   your Cloud Console machine.
3. In ``main.tf``, change the project variable to your ``project ID``.
   Change any other variables, if necessary.
4. Download the key in JSON format for the service account created in ``Step 1``
   to your project's Cloud Console machine. Rename it
   to ``service_account.json``.
5. Run ``terraform apply``. After this command finishes, it should
   output the URL to FLINT Cloud (ingress).

To tear down the infrastructure and delete the application, run
``terraform destroy`` in the same directory where ``main.tf`` is
present. If this fails, run it again.

.. _Terraform: https://www.terraform.io/

Azure
-----

To deploy FLINT.Cloud to Azure, we recommend using the Azure App Service
with a custom Microsoft Container Registry container built from our
``local`` directory. This setup uses `Azure CLI`_ to
deploy the infrastructure and the applications to be used. You need to 
sign in to the Azure CLI by using the ``az login`` command. To
finish the authentication process, follow the steps displayed in your
terminal. To build images, we use `Docker`_ and then push them to `Azure Container Registry`_.

Download the project
~~~~~~~~~~~~~~~~~~~~

Clone the repository:

.. code:: sh

   git clone https://github.com/moja-global/flint.cloud

Navigate to the ``local`` directory:

.. code:: sh

   sh local

Build the images locally
~~~~~~~~~~~~~~~~~~~~~~~~

To build the ``rest_api_gcbm`` image locally, run the following command:

.. code:: sh

   pushd rest_api_gcbm
   docker build --build-arg BUILD_TYPE=RELEASE --build-arg NUM_CPU=4 -t gcbm-api .
   popd

To build the ``rest_api_flint.example`` image locally, run the following
command:

.. code:: sh

   pushd rest_api_flint.example
   docker build -t flint-api .
   popd

Create a resource group
~~~~~~~~~~~~~~~~~~~~~~~

To push images onto and deploy containers with the Azure App 
Service, you need to first prepare some resources. Start by
creating a resource group that will collect all your
resources.

.. code:: sh

   az group create --name myResourceGroup --location centralindia

You can change the ``--location`` value to specify a region near you.

Create a Container Registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can now push the image to Azure Container Registry so that App
Service can deploy it. Create an Azure Container Registry to push your
images to:

.. code:: sh

   az acr create --name <registry-name> --resource-group myResourceGroup --sku Basic --admin-enabled true

Replace ``<registry-name>`` with a suitable name for your registry. The
name must contain only letters and numbers, and must be unique across all
of Azure.

Retrieve your credentials for the Container Registry:

.. code:: sh

   az acr credential show --resource-group myResourceGroup --name <registry-name>

Use the ``docker login`` command to sign in to the container registry:

.. code:: sh

   docker login <registry-name>.azurecr.io --username <registry-username>

Replace ``<registry-name>`` and ``<registry-username>`` with values from
the previous steps. When prompted, type in one of the passwords from the
previous step.

Tag the images with the registry name:

.. code:: sh

   docker tag rest_api_gcbm <registry-name>.azurecr.io/rest_api_gcbm:latest
   docker tag rest_api_flint.example <registry-name>.azurecr.io/rest_api_flint.example:latest

Use the docker push command to push the image to the registry:

.. code:: sh

   docker push <registry-name>.azurecr.io/rest_api_gcbm:latest
   docker push <registry-name>.azurecr.io/rest_api_flint.example:latest

Use the ``az acr repository list`` command to verify that the push was
successful:

.. code:: sh

   az acr repository list -n <registry-name>

Deploy the image from registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To deploy a container to Azure App Service, you first create a web app
on App Service, then connect the web app to the container registry. When
the web app starts, App Service automatically pulls the image from the
registry.

Create an App Service plan using the ``az appservice plan create``
command:

.. code:: sh

   az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --is-linux

Create the web app with the ``az webpp create`` command. Since we are
deploying two images to two different web apps, you need to
enter these commands twice. To deploy ``rest_api_gcbm`` to the first
web app and ``rest_api_flint.example`` to the second web app, run the
following commands:

.. code:: sh

   az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name <app-name-1> --deployment-container-image-name <registry-name>.azurecr.io/rest_api_gcbm:latest
   az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name <app-name-2> --deployment-container-image-name <registry-name>.azurecr.io/rest_api_flint.example:latest

Use the ``az webapp config appsettings set`` to set the
``WEBSITES_PORT`` environment variable. In
our case, the port to be exposed is ``8080``.

.. code:: sh

   az webapp config appsettings set --resource-group myResourceGroup --name <app-name-1> --settings WEBSITES_PORT=8080
   az webapp config appsettings set --resource-group myResourceGroup --name <app-name-2> --settings WEBSITES_PORT=8080

Enable the system-assigned managed identity for the web app by using the
``az webapp identity assign`` command:

.. code:: sh

   az webapp identity assign --resource-group myResourceGroup --name <app-name-1> --query principalId --output tsv
   az webapp identity assign --resource-group myResourceGroup --name <app-name-2> --query principalId --output tsv

Replace ``<app-name>`` with the name you used in the previous step. The
output of the command (filtered by the ``--query`` and ``--output``
arguments) is the service principal of the assigned identity.

Retrieve your subscription ID with the ``az account show`` command,
which you need in the next step:

.. code:: sh

   az account show --query id --output tsv

Grant the managed identity permission to access the container registry:

.. code:: sh

   az role assignment create --assignee <principal-id> --scope /subscriptions/<subscription-id>/resourceGroups/myResourceGroup/providers/Microsoft.ContainerRegistry/registries/<registry-name> --role "AcrPull"

Replace the following values:

-  ``<principal-id>`` with the service principal ID from the
   ``az webapp identity assign`` command.
-  ``<registry-name>`` with the name of your container registry.
-  ``<subscription-id>`` with the subscription ID retrieved from the
   ``az account show`` command.

Make sure the above steps are repeated for both of the apps that you are
going to deploy. Configure your app to use the managed identity to pull
from Azure Container Registry.

.. code:: sh

   az resource update --ids /subscriptions/<subscription-id>/resourceGroups/myResourceGroup/providers/Microsoft.Web/sites/<app-name-1>/config/web --set properties.acrUseManagedIdentityCreds=True
   az resource update --ids /subscriptions/<subscription-id>/resourceGroups/myResourceGroup/providers/Microsoft.Web/sites/<app-name-2>/config/web --set properties.acrUseManagedIdentityCreds=True

Replace the following values:

-  ``<subscription-id>`` with the subscription ID retrieved from the az
   account show command.
-  ``<app-name>`` with the name of your web app.

Deploy the image
~~~~~~~~~~~~~~~~

Use the ``az webapp config container set`` command to specify the
container registry and the image to deploy for the web app:

.. code:: sh

   az webapp config container set --name <app-name-1> --resource-group myResourceGroup --docker-custom-image-name <registry-name>.azurecr.io/rest_api_gcbm:latest --docker-registry-server-url https://<registry-name>.azurecr.io
   az webapp config container set --name <app-name-2> --resource-group myResourceGroup --docker-custom-image-name <registry-name>.azurecr.io/rest_api_flint.example:latest --docker-registry-server-url https://<registry-name>.azurecr.io

Replace ``<app-name-1>`` and ``<app-name-2>`` with the name of your web
app, and replace all instances of ``<registry-name>`` with the name of your
registry. When the ``az webapp config container set`` command completes,
the web app is running in the container on App Service.

To test the app, browse to ``https://<app-name>.azurewebsites.net``,
replacing ``<app-name>`` with the name of your web app. To clean up the
resources, you only need to delete the resource group that contains
them:

.. code:: sh

   az group delete --name myResourceGroup

.. _Azure CLI: https://docs.microsoft.com/en-us/cli/azure/
.. _Docker: https://www.docker.com/
.. _Azure Container Registry: https://azure.microsoft.com/en-in/services/container-registry/
