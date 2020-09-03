# FROM jupyter/scipy-notebook:04f7f60d34a6
FROM elyra/kernel-spark-py:2.0.0rc2

ENV PATH=$PATH:$CONDA_DIR/bin

USER root

#    jupyter_client \
RUN conda install --quiet --yes \
    cffi \
    ipykernel \
    ipython \
    future \
    pycryptodomex && \
    conda clean -tipsy && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

RUN apt-get update && apt-get install -yq --no-install-recommends \
    vim \
    libkrb5-dev \
    && rm -rf /var/lib/apt/lists/*

RUN cd && \
  git clone https://github.com/takluyver/jupyter_protocol && \
  cd jupyter_protocol && \
  pip install -e .
RUN cd && \
  git clone https://github.com/takluyver/jupyter_kernel_mgmt && \
  cd jupyter_kernel_mgmt && \
  pip install -e .
RUN cd && \
  git clone https://github.com/gateway-experiments/remote_kernel_provider && \
  cd remote_kernel_provider && \
  pip install -e .
RUN cd && \
  git clone https://github.com/gateway-experiments/kubernetes_kernel_provider && \
  cd kubernetes_kernel_provider && \
  pip install -e .

RUN pip install --ignore-installed -U terminado

RUN cd && \
  git clone https://github.com/datalayer-contrib/jupyter_server --branch jupyter-kernel-mgmt-master && \
  cd jupyter_server && \
  pip install -e .

# ADD docker_kernelspecs.tar /usr/local/share/jupyter/kernels/

# RUN cd && \
#   export IR=https://github.com/gateway-experiments/remote_kernel_provider/releases/download/tag/v0.3.0 && \
#   mkdir /usr/local/share/jupyter/kernels && \
#   cd  /usr/local/share/jupyter/kernels && \
#   curl $IR/yarn_kernelspecs.tar | tar xvf -

# RUN chown jovyan:users /usr/local/bin/bootstrap-kernel.sh && \
# 	chmod 0755 /usr/local/bin/bootstrap-kernel.sh && \
# 	chown -R jovyan:users /usr/local/bin/kernel-launchers
# ENV KERNEL_LANGUAGE python
# RUN /usr/local/bin/bootstrap-kernel.sh

# RUN cd && \
#   cd enterprise_gateway && \
#   mkdir -p /usr/local/share/jupyter/kernels && \
#   cp -r etc/kernelspecs/spark_python_kubernetes /usr/local/share/jupyter/kernels/ && \
#   cp -r etc/kernel-launchers/kubernetes/scripts /usr/local/share/jupyter/kernels/spark_python_kubernetes/

RUN pip install --pre jupyterlab

RUN jupyter k8s-kernelspec install && \
    jupyter k8s-kernelspec install --spark
#    jupyter k8s-kernelspec install --tensorflow && \
#    jupyter k8s-kernelspec install --language=R && \
#    jupyter k8s-kernelspec install --language=R --spark && \
#    jupyter k8s-kernelspec install --language=Scala && \
#    jupyter k8s-kernelspec install --language=Scala --spark

RUN mv /usr/local/share/jupyter/kernels/k8skp_python/k8skp_kernel.json /usr/local/share/jupyter/kernels/k8skp_python/kernel.json
RUN mv /usr/local/share/jupyter/kernels/k8skp_python_spark/k8skp_kernel.json /usr/local/share/jupyter/kernels/k8skp_python_spark/kernel.json

# RUN cd && \ 
#   git clone https://github.com/gateway-experiments/notebook && \
#   cd notebook && \
#   pip install -e .

# ENV IR https://github.com/gateway-experiments/remote_kernel_provider/releases/download/v0.1-interim-dev/
# RUN pip install \
#   ${IR}/notebook-6.0.0.dev0-py2.py3-none-any.whl

RUN chown -R jovyan:users /usr/local/share/jupyter && chmod -R go+rX /usr/local/share/jupyter/kernels/

ENTRYPOINT ["tini", "-g", "--"]

# CMD ["jupyter", "notebook", "--debug", "--NotebookApp.token=''", "--NotebookApp.password=''"]
CMD ["jupyter", "lab", "--debug", "--LabApp.token="]

USER jovyan
