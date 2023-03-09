FROM python:3.10.9-slim-buster

WORKDIR /src

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN pip install -U --upgrade pip
RUN pip install --upgrade -r /tmp/requirements.txt

COPY . /src/sgde_frontend

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "sgde_frontend/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
