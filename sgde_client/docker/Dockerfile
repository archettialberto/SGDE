FROM tensorflow/tensorflow:2.12.0-gpu-jupyter

RUN apt-get update && apt clean

COPY sgde_client/docker/requirements.txt /tmp/requirements.txt

RUN pip install -U --upgrade pip
RUN pip install -r /tmp/requirements.txt

# Enable Jupyter
RUN mkdir -p /.local
RUN chmod -R 777 /.local

WORKDIR /src

CMD ["/bin/bash"]
