FROM python:3.10-bullseye

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && apt-get install -y nmap iputils-ping iproute2 net-tools

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server and client tools (clients are optional inside the image)
#COPY nmap_client.py /app/nmap_client.py
#COPY clients/server_all.py /app/server_all.py
COPY clients /app

#EXPOSE 502

# Keep it simple: run the combined server
#CMD ["python", "/app/server_all.py test"]
