FROM tensorflow/tensorflow:latest-gpu-jupyter

WORKDIR /src

RUN apt-get update && apt clean

COPY ./sgde_client/requirements.txt /tmp/requirements.txt

RUN pip install -U --upgrade pip
RUN pip install -r /tmp/requirements.txt

COPY ./schemas.py /src
COPY ./sgde_client /src/sgde_client

RUN mkdir -p ./local
RUN chmod -R 777 /.local

CMD ["/bin/bash"]
