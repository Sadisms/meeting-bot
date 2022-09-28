FROM python:3.10.7-slim-buster
RUN apt-get update && apt-get install -y git
WORKDIR /meeting-bot
copy . /meeting-bot
RUN pip3 install -r requirements.txt
RUN pip3 install -r custom_reqs.txt