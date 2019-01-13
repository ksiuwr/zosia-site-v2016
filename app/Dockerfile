FROM python:3.6
ARG DJANGO_ENV

ENV PYTHONUNBUFFERED 1
ENV NODE_PATH=/node_modules
ENV DJANGO_ENV=${DJANGO_ENV}
ENV DJANGO_SETTINGS_MODULE="zosia16.settings.${DJANGO_ENV}"

WORKDIR /code

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get update && apt-get upgrade -y && apt-get -y install nodejs

ADD requirements.txt /code/
RUN pip install -r requirements.txt

# FIXME the FE build is overcomplicated with all the tools like make,
# bower, npm and webpack and copying files around, as well as mounting
# volumes (in dev environment) and should be simplified (npm/yarn + webpack?)
# this would also allow us to use webpack dev server in dev env
ADD package.json /code/
ADD Makefile /code/
ADD webpack.config.js /code/
ADD static /code/static
RUN npm install && make deps
RUN cp -R /code/static/bower_components /bower_components && cp -R /code/node_modules /node_modules
RUN ln -s /dev/stderr /var/log/django.log

ADD . /code/

EXPOSE 8000
