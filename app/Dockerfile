FROM node:16-alpine AS node-builder

WORKDIR /code

COPY package.json /code/
COPY webpack.config.js /code/
COPY yarn.lock /code/
COPY static /code/static
COPY js /code/js

RUN yarn install
RUN yarn build

# Main image
FROM python:3.8-buster

# Uncomment if you need to install any additional package
# RUN set -x \
# 	  && apt-get update \
#     && apt-get install --no-install-recommends --no-install-suggests -y ??? \
#     && apt-get autoremove -y \
#     && rm -rf /var/lib/apt/lists/* \
#     && rm -rf /root/.cache* \
#     && rm -rf /tmp/* \
# ;

ARG DJANGO_ENV
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV=${DJANGO_ENV}
ENV DJANGO_SETTINGS_MODULE="zosia16.settings.${DJANGO_ENV}"

WORKDIR /code

COPY uwsgi.ini /code
COPY run.sh /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY --from=node-builder /code/static /static

COPY src /code/

EXPOSE 8000
