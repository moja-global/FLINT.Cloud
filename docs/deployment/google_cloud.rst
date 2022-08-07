.. _Deployment:

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