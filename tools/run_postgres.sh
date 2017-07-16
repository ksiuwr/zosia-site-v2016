#!/bin/bash
set -e
NAME=zosia16-postgres
IMAGE=postgres:9.5
if docker inspect $NAME;
then
  docker start $NAME
else
  docker run -d --name $NAME -p 5432:5432 $IMAGE
fi
