# JupyterLab with Kubernetes Kernel Provider Example

> Most this work in this example has been taken and inspired from https://github.com/gateway-experiments/remote_kernel_provider/releases/tag/v0.1-interim-dev. Thank you @kevin-bates for this!

You will need a working [minikube](https://kubernetes.io/docs/setup/learning-environment/minikube/) and [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl) environment.

Follow the next steps.

```bash
# Prepare your minikube env (ensure you set your docker-env).
minikube start
eval $(minikube docker-env) # This is important!
```

```bash
# Build the docker image in the minikube docker-env.
make build
```

```bash
# Deploy jupyterlab.
make install
# Get URL to access jupyterlab via a Browser.
make url
# http://192.168.64.3:31238
```

Open the printed URL in your browser and use `JupyterLab`.

When you create a notebook and run some code, `Kubernetes` will launch for you a separated pod.

You can check this with `kubectl`.

```bash
kubectl get pods -n jupyterlab
# NAME                                          READY   STATUS    RESTARTS   AGE
# jovyan-32731cf2-017a-4cb4-bd9d-1d414bee9475   1/1     Running   0          3m22s
# jupyterlab-d98658b8b-gsn4v                    1/1     Running   0          3m33s
# kernel-image-puller-9z6zh                     1/1     Running   0          3m33s
```

```bash
# When you are done, remove for the posterity.
make rm
```
