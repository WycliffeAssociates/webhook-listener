FROM python:3.7-slim-stretch
COPY . /webhooks/
RUN apt update && apt install -y build-essential libssl-dev git libffi-dev python3-dev freetds-dev && rm -rf /var/lib/apt/lists/* 
RUN pip3 install -r /webhooks/requirements.txt
WORKDIR /webhooks/
ENTRYPOINT [ "python", "./app/main.py" ]
