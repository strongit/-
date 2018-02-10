FROM ubuntu:14.04
MAINTAINER promisejohn

ENV DEBIAN_FRONTEND noninteractive

# Install Python Setuptools
RUN apt-get -y update && apt-get -y install python2.7 python-pip python-dev build-essential && pip install --upgrade pip

# add files and folders
ADD . /src
ADD pip.conf /etc/pip.conf

# change current workspace
WORKDIR /src

# install dependencies
RUN pip install -r requirements.txt

# init db structure and data
RUN python scripts/manager.py initdb
RUN python scripts/manager.py importdata

CMD ["python", "runserver.py"]
