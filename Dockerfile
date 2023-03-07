FROM python:3.10

WORKDIR /exp

RUN apt-get upgrade & apt-get update

COPY ./requirements.txt /exp/.req/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /exp/.req/requirements.txt

COPY ./src /exp/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
