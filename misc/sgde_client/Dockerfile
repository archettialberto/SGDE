FROM tensorflow/tensorflow:latest-gpu-jupyter

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /sgde_api/requirements.txt

COPY ../* /src/sgde_client

CMD ["/bin/bash"]
