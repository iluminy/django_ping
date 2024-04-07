# base image
FROM python:3.10
# setup environment variable
ENV DockerHOME=/home/app/django_ping

# set work directory
RUN mkdir -p $DockerHOME

# where code lives
WORKDIR $DockerHOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=django_ping.settings

# upgrade pip
RUN pip install --upgrade pip

ADD ./requirements.txt $DockerHOME/requirements.txt
# install all dependencies
RUN pip install -r requirements.txt
# copy whole project to home directory
COPY . $DockerHOME

# install ping utility
RUN apt-get update && apt-get install -y iputils-ping
