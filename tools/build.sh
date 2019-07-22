#!/usr/bin/env bash

HELP_TEXT="Build the docker images for zosia.
Usage:
    ./build.sh [options]

Options:
    --no-cache  - don't use docker cache while building the images
    --tag TAG   - tag resulting images with zosia:<TAG> instead of zosia:latest
    --verbose   - verbose output, useful for debugging purposes
"

NO_CACHE=""
TAG="latest"
VERBOSE=""

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --help)
    echo "${HELP_TEXT}"
    exit 0
    ;;
    --no-cache)
    NO_CACHE="--no-cache"
    shift
    ;;
    --tag)
    shift
    TAG="$1"
    shift
    ;;
    --verbose)
    VERBOSE="--verbose"
    shift
    ;;
    *)
    echo "Argument $1 is not supported."
    echo "${HELP_TEXT}"
    exit 1
    ;;
esac
done

export TAG=${TAG}

COMPOSE_FILENAME="docker-compose.dev.yml"
CONTAINER_NAME="zosia_dev:${TAG}"

echo "Running build using ${COMPOSE_FILENAME} and tagging containers with ${CONTAINER_NAME}"
docker-compose ${VERBOSE} -f ../${COMPOSE_FILENAME} build ${NO_CACHE}