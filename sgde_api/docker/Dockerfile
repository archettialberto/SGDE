FROM python:3.10.9-slim-buster

WORKDIR /src

RUN apt-get update && apt clean

COPY ./sgde_api/docker/requirements.txt /tmp/requirements.txt

RUN pip install -U --upgrade pip
RUN pip install -r /tmp/requirements.txt

COPY ./schemas.py /src
COPY ./sgde_api /src/sgde_api

EXPOSE 8000

CMD ["uvicorn", "sgde_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
