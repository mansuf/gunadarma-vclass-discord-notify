FROM ubuntu:latest

COPY . /app
COPY ./credential-user.secret.json /app
COPY ./credential-db.secret.json /app
COPY ./bot-token.secret.txt /app

WORKDIR /app

RUN apt-get update
RUN apt-get install python3 python3-pip python3-dev default-libmysqlclient-dev build-essential nginx -y
RUN pip install -r requirements.txt --no-input

# Timezone
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Jakarta /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata