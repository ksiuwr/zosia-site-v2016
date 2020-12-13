
FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV NODE_PATH=/node_modules
ENV DJANGO_ENV=${DJANGO_ENV}
ENV DJANGO_SETTINGS_MODULE="zosia16.settings.dev"

# install nodejs and npm
RUN set -x \
    && curl -sL https://deb.nodesource.com/setup_10.x | bash - \
	&& apt-get update \
    && apt-get install -y nodejs --no-install-recommends \
    && npm install -g yarn \
    ;

COPY requirements.txt /code/
RUN pip install -r /code/requirements.txt

COPY package.json /code/
COPY webpack.config.js /code/
COPY yarn.lock /code/
COPY static /code/static
COPY js /code/js

WORKDIR /code
