#!/usr/bin/env bash

HELP_TEXT="Run the zosia docker containers for local development.
Usage:
    ./run.sh [options]

Options:
    --build     - build images before running.
    --no-cache  - (only used with --build) don't use docker cache while
                  building the images.
    --tag TAG   - run zosia:<TAG> images instead of zosia:latest. Also tags the
                  resulting images if --build option is specified
    --verbose   - verbose output, useful for debugging purposes
    --help      - prints this help message
"

BUILD=0
NO_CACHE=""
TAG="latest"
VERBOSE=""

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --build)
    BUILD=1
    shift
    ;;
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

export COMPOSE_HTTP_TIMEOUT=200

if [[ ${BUILD} -eq 1 ]]; then
    ./build.sh ${NO_CACHE} ${VERBOSE} --tag ${TAG}
    if [[ $? -ne 0 ]]; then
        echo "ERROR while building images"
        exit 1
    fi
fi

export TAG=${TAG}
echo "Running containers"
docker-compose ${VERBOSE} -f ../docker-compose.dev.yml -p zosia up
