FROM ubuntu:24.04

RUN apt-get update; apt-get install -y python3; apt install -y python3-pip; rm -rf var/cache/apt

WORKDIR /src

COPY . /src

RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

EXPOSE 5000:5000/tcp

# why don't we need to set up venv on Docker?
