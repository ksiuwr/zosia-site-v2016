FROM python:3
ENV PYTHONUNBUFFERED 1
ENV NODE_PATH=/node_modules
WORKDIR /code

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get -y install nodejs

ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD package.json /code/
RUN npm install && mv /code/node_modules /node_modules
ADD . /code/
