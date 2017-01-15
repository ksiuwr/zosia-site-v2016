#!/bin/bash
set -e
NAME=zosia16-postgres
IMAGE=postgres:9.5

docker exec $NAME createuser -U postgres zosia
docker exec $NAME createdb -U postgres --owner zosia zosia
