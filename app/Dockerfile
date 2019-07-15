FROM node:alpine AS node-builder

WORKDIR /code

ADD package.json /code/
ADD webpack.config.js /code/
ADD static /code/static

RUN yarn install
RUN yarn build

# Main image
FROM python:3.6-buster

# Uncomment if you need to install any additional package
# RUN set -x \
# 	&& apt-get update \
#     && apt-get install --no-install-recommends --no-install-suggests -y ??? \
#     && apt-get autoremove -y \
#     && rm -rf /var/lib/apt/lists/* \
#     && rm -rf /root/.cache* \
#     && rm -rf /tmp/* \
# ;

ARG DJANGO_ENV
ENV PYTHONUNBUFFERED 1
ENV NODE_PATH=/node_modules
ENV DJANGO_ENV=${DJANGO_ENV}
ENV DJANGO_SETTINGS_MODULE="zosia16.settings.${DJANGO_ENV}"

WORKDIR /code

ADD requirements.txt /code/
RUN pip install -r requirements.txt

COPY --from=node-builder /code/node_modules /node_modules
COPY --from=node-builder /code/static /code/static

ADD . /code/

EXPOSE 8000
