FROM python:3.10-bullseye

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && apt-get install -y nmap iputils-ping iproute2 net-tools

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY clients /app

RUN mkdir -p /app/reports


