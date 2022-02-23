FROM python:3.8
ENV PYTHONUNBUFFERED=1
WORKDIR /cars_drf_docker
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt