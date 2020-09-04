FROM jupyter/scipy-notebook:04f7f60d34a6
# FROM elyra/kernel-spark-py:2.2.0rc2

ENV PATH=$PATH:$CONDA_DIR/bin

USER root

RUN conda install --quiet --yes \
    cffi \
    ipykernel \
    ipython \
    future \
    pycryptodomex

RUN apt-get update && apt-get install -yq --no-install-recommends \
    vim \
    libkrb5-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --ignore-installed -U terminado
RUN pip uninstall -y jupyter_client

RUN cd && \
  git clone https://github.com/takluyver/jupyter_protocol jupyter_protocol && \
  cd jupyter_protocol && \
  pip install -e .
RUN cd && \
  git clone https://github.com/takluyver/jupyter_kernel_mgmt jupyter_kernel_mgmt && \
  cd jupyter_kernel_mgmt && \
  pip install -e .
#  git clone https://github.com/gateway-experiments/remote_kernel_provider && \
RUN cd && \
  git clone https://github.com/datalayer-contrib/jupyter-kernel-provider-remote remote_kernel_provider --branch debug && \
  cd remote_kernel_provider && \
  git checkout 855875a -b 855875a && \
  pip install -e .
#  git clone https://github.com/gateway-experiments/kubernetes_kernel_provider && \
RUN cd && \
  git clone https://github.com/datalayer-contrib/jupyter-kernel-provider-k8s kubernetes_kernel_provider --branch debug && \
  cd kubernetes_kernel_provider && \
  pip install -e .

RUN jupyter k8s-kernelspec install
#    jupyter k8s-kernelspec install --spark
#    jupyter k8s-kernelspec install --tensorflow && \
#    jupyter k8s-kernelspec install --language=R && \
#    jupyter k8s-kernelspec install --language=R --spark && \
#    jupyter k8s-kernelspec install --language=Scala && \
#    jupyter k8s-kernelspec install --language=Scala --spark

#  git clone https://github.com/kevin-bates/jupyter_server --branch jupyter-kernel-mgmt && \
RUN cd && \
  git clone https://github.com/datalayer-contrib/jupyter-server jupyter_server --branch jupyter-kernel-mgmt-master && \
  cd jupyter_server && \
  pip install -e .

RUN pip install --pre --upgrade jupyterlab

RUN conda clean -tipsy && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

RUN chown -R jovyan:users /usr/local/share/jupyter && \
  chown -R jovyan:users /home/jovyan && \
  chmod -R go+rX /usr/local/share/jupyter/kernels

USER jovyan

ENTRYPOINT ["tini", "-g", "--"]

CMD ["jupyter", "lab", "--ip", "0.0.0.0", "--debug", "--LabApp.token="]
