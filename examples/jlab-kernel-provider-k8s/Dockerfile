# FROM jupyter/scipy-notebook:04f7f60d34a6
FROM elyra/kernel-spark-py:2.0.0rc2

ENV PATH=$PATH:$CONDA_DIR/bin

USER root

# RUN conda install --quiet --yes \
#     cffi \
#     ipykernel \
#     ipython \
#     jupyter_client \
 #    future \
#     pycryptodomex && \
#     conda clean -tipsy && \
#     fix-permissions $CONDA_DIR && \
#     fix-permissions /home/$NB_USER

# RUN apt-get update && apt-get install -yq --no-install-recommends \
#     libkrb5-dev \
#    && rm -rf /var/lib/apt/lists/*

RUN cd && \
  git clone https://github.com/takluyver/jupyter_protocol && \
  cd jupyter_protocol && \
  pip install -e .
RUN cd && \
  git clone https://github.com/takluyver/jupyter_kernel_mgmt && \
  cd jupyter_kernel_mgmt && \
  pip install -e .
RUN cd && \
  git clone https://github.com/gateway-experiments/kubernetes_kernel_provider && \
  cd kubernetes_kernel_provider && \
  pip install -e .

# RUN cd && \ 
#   git clone https://github.com/gateway-experiments/notebook && \
#   cd notebook && \
#   pip install -e .
RUN pip install --pre jupyterlab

RUN pip install --ignore-installed -U terminado
RUN cd && \
  git clone https://github.com/datalayer-contrib/jupyter_server --branch jupyter-kernel-mgmt-master && \
  cd jupyter_server && \
  pip install -e .

# ADD jupyter_enterprise_gateway_kernel_image_files*.tar.gz /usr/local/bin/
# RUN cd && \
#   export IR=https://github.com/gateway-experiments/remote_kernel_provider/releases/download/tag/v0.3.0 && \
#   mkdir /usr/local/share/jupyter/kernels && \
#   cd  /usr/local/share/jupyter/kernels && \
#   curl $IR/yarn_kernelspecs.tar | tar xvf -

RUN cd && \
  git clone https://github.com/jupyter/enterprise_gateway && \
  cd enterprise_gateway && \
  pip install -e .

# RUN jupyter k8s-kernelspec install
#    jupyter k8s-kernelspec install --spark && \
#    jupyter k8s-kernelspec install --tensorflow && \
#    jupyter k8s-kernelspec install --language=R && \
#    jupyter k8s-kernelspec install --language=R --spark && \
#    jupyter k8s-kernelspec install --language=Scala && \
#    jupyter k8s-kernelspec install --language=Scala --spark

RUN cd && \
  cd enterprise_gateway && \
  mkdir -p /usr/local/share/jupyter/kernels && \
  cp -r etc/kernelspecs/spark_python_kubernetes /usr/local/share/jupyter/kernels/ && \
  cp -r etc/kernel-launchers/kubernetes/scripts /usr/local/share/jupyter/kernels/spark_python_kubernetes/

# RUN chown jovyan:users /usr/local/bin/bootstrap-kernel.sh && \
# 	chmod 0755 /usr/local/bin/bootstrap-kernel.sh && \
# 	chown -R jovyan:users /usr/local/bin/kernel-launchers
# ENV KERNEL_LANGUAGE python
# RUN /usr/local/bin/bootstrap-kernel.sh

# ADD docker_kernelspecs.tar /usr/local/share/jupyter/kernels/

# RUN pip install --upgrade tornado==5.1.1 && \
#   pip install kubernetes_kernel_provider && \
#   pip install /tmp/docker_kernel_provider-0.1.0.dev0-py3-none-any.whl && \
#   pip install /tmp/notebook-6.0.0.dev0-py2.py3-none-any.whl && \
#   pip freeze > /tmp/requirements.txt && cat /tmp/requirements.txt

RUN chown -R jovyan:users /usr/local/share/jupyter && chmod -R go+rX /usr/local/share/jupyter/kernels/

ENTRYPOINT ["tini", "-g", "--"]

CMD ["jupyter", "lab", "--debug", "--LabApp.token="]

USER jovyan
