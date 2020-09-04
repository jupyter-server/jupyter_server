# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

build:
	docker build \
		-t jupyter/jlab-k8s-provider-example:0.0.1 \
		.

install:
	kubectl apply -f jlab.yaml

url:
	@exec minikube service jupyterlab --url -n jupyterlab

rm:
	kubectl delete -f jlab.yaml
