# REST API GCBM integration for Kubernetes

This Kubernetes-based setup provisions a local installation of GCBM REST API on Minikube which uses a local `gcbm-api` image on your machine.

## Installation

1. [Install Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) to run Kubernetes locally.

2. Start your cluster on minikube, by running the command:
	 ```sh
	 minikube start
	 ```
	 It starts a local Kubernetes cluster.
3. Before starting the local dev/test deployment run:
	```sh
	eval $(minikube docker-env)
	```
	This command sets up Docker to use the same Docker daemon as your Minikube cluster does. This means images you build are directly available to the cluster.
4. Clone the repository and build the `gcbm-api` image on your machine:
	```sh
	git clone git@github.com:moja-global/FLINT.Cloud.git
	cd FLINT.Cloud && cd local/rest_api_gcbm
	docker build -t gcbm-api .
	```
5. Navigate to `kubernetes/rest_api_gcbm` directory and create a deployment:
	```sh
	cd kubernetes/rest_api_gcbm
	kubectl create -f gcbm-api.yml
	```
6. Check the running pods and deployment:
	```sh
	kubectl get pods
	kubectl get deployment
	```
	Status should be running on pods. If not then please troubleshoot using  `kubectl describe pod <Pod-Name>`.
7. Expose the service:
	```sh
	kubectl expose deployment gcbm-api --type=NodePort --port=8080
	```
8. Check if the `gcbm-api` service is exposed:
	```sh
	kubectl get svc
	```
9. Create the ingress:
	```sh
	kubectl create -f ingress.yml
	```
10. Forward requests on port 8080:
	```sh
	kubectl port-forward service/gcbm-api 8080:8080
	```

Navigate to `localhost:8080` to check the running API.
