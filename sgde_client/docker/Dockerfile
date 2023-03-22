FROM tensorflow/tensorflow:latest-gpu-jupyter

WORKDIR /exp

RUN apt-get update && apt clean

COPY ./sgde_client/docker/requirements.txt /tmp/requirements.txt

RUN pip install -U --upgrade pip
RUN pip install -r /tmp/requirements.txt

# COPY ./schemas.py /src
# COPY ./sgde_client /src/sgde_client
# COPY ./sgde_demo.ipynb /src

RUN mkdir -p /.local
RUN chmod -R 777 /.local

CMD ["/bin/bash"]
