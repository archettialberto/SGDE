FROM python:3.10

WORKDIR /src

RUN apt-get upgrade & apt-get update

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ../* /src/sgde_server

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
