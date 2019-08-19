FROM node:8.16-stretch-slim AS md_builder
RUN apt-get update && \
    apt-get install -y git && \
    git clone https://github.com/WycliffeAssociates/badge-markdown-generator /badge-markdown-generator
WORKDIR /badge-markdown-generator
RUN npm install --production && npm run build

FROM python:3.7-stretch
COPY . /webhooks/
COPY --from=md_builder /badge-markdown-generator/build /webhooks/app/md
RUN apt-get update && apt-get install -y wget apt-transport-https && \
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.asc.gpg && \
    mv microsoft.asc.gpg /etc/apt/trusted.gpg.d/ && \
    wget -q https://packages.microsoft.com/config/debian/9/prod.list && \
    mv prod.list /etc/apt/sources.list.d/microsoft-prod.list && \
    chown root:root /etc/apt/trusted.gpg.d/microsoft.asc.gpg && \
    chown root:root /etc/apt/sources.list.d/microsoft-prod.list && \
    apt-get update && \
    apt-get install -y build-essential aspnetcore-runtime-2.2 libssl-dev git libffi-dev python3-dev freetds-dev && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install -r /webhooks/requirements.txt
WORKDIR /webhooks/app/
CMD ["gunicorn", "--access-logfile", "-", "-b", "0.0.0.0:80", "app"]
