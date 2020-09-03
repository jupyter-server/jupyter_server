# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

build:
	docker build \
		-t jupyter-server/k8-provider-example:0.0.1 \
		.

install:
	kubectl apply -f jlab.yaml

jlab:
	minikube service jupyterlab --url -n jupyterlab
	# Get the token via the pod...
	# kubectl exec jupyterlab-d5587599b-9tmlj -n jupyterlab -i -t -- jupyter notebook list

rm:
	kubectl delete -f jupyterlab.yaml
