
FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV NODE_PATH=/node_modules
ENV DJANGO_ENV=${DJANGO_ENV}
ENV DJANGO_SETTINGS_MODULE="zosia16.settings.dev"

# install nodejs and npm
RUN set -x \
    && curl -sL https://deb.nodesource.com/setup_10.x | bash - \
	&& apt-get update \
    && apt upgrade -y \
    && apt install -y nodejs \
    && npm install -g yarn \
    ;

ADD package.json /code/
ADD webpack.config.js /code/
ADD yarn.lock /code/
ADD static /code/static
ADD js /code/js
ADD requirements.txt /code/
RUN pip install -r /code/requirements.txt

WORKDIR /code

