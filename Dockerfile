FROM python:3.7-stretch
COPY . /webhooks/
RUN apt-get install -y wget
RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.asc.gpg && mv microsoft.asc.gpg /etc/apt/trusted.gpg.d/ && wget -q https://packages.microsoft.com/config/debian/9/prod.list && mv prod.list /etc/apt/sources.list.d/microsoft-prod.list && chown root:root /etc/apt/trusted.gpg.d/microsoft.asc.gpg && chown root:root /etc/apt/sources.list.d/microsoft-prod.list
RUN apt update && apt install -y apt-transport-https && apt update && apt install -y build-essential aspnetcore-runtime-2.2 libssl-dev git libffi-dev python3-dev freetds-dev && rm -rf /var/lib/apt/lists/* 
RUN pip3 install -r /webhooks/requirements.txt
WORKDIR /webhooks/
ENTRYPOINT [ "python", "./app/main.py" ]
