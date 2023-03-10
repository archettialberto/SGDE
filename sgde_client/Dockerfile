FROM tensorflow/tensorflow:latest-gpu-jupyter

WORKDIR /src

RUN apt-get update && apt clean

COPY requirements.txt /tmp/requirements.txt

RUN pip install -U --upgrade pip
RUN pip install -r /tmp/requirements.txt

COPY . /src/sgde_client

RUN mkdir -p ./local
RUN chmod -R 777 /.local

CMD ["/bin/bash"]