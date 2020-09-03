# JupyterLab Kubernetes Kernel Provider Example

Most this work has been taken and inspired by https://github.com/gateway-experiments/remote_kernel_provider/releases/tag/v0.1-interim-dev

A working [minikube](https://kubernetes.io/docs/setup/learning-environment/minikube/) and [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl) environment is required.

```
minikube start
eval $(minikube docker-env) 
make build
make install
make jlab
make rm
```
