FROM python:3.10.7-slim-buster

workdir /app
COPY . /app/
RUN pip install -r requirements.txt