#!/usr/bin/env bash

HELP_TEXT="Push docker images to ECR.

Usage:
    ./upload.sh [options]

Options:
    --build     - build images before running.
    --no-cache  - (only used with --build) don't use docker cache while
                  building the images.
    --tag TAG   - run zosia:<TAG> images instead of zosia:latest. Also tags the
                  resulting images if --build option is specified
    --verbose   - verbose output, useful for debugging purposes
    --help      - prints this help message
"

DOCKER_REPO_URI_BASE="463715963173.dkr.ecr.eu-central-1.amazonaws.com"

TAG="latest"

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

# ./install_awscli.sh

# if [[ ${BUILD} -eq 1 ]]; then
#     ./build.sh --prod ${NO_CACHE} ${VERBOSE} --tag ${TAG}
#     if [[ $? -ne 0 ]]; then
#         echo "ERROR while building images"
#         exit 1
#     fi
# fi

# DOCKER_LOGIN_CMD=`aws ecr get-login --no-include-email --profile zosia | sed 's|https://||'`
# echo "Logging to remote registry with command"
# echo ${DOCKER_LOGIN_CMD}
# eval ${DOCKER_LOGIN_CMD}

# upload zosia_web image
ZOSIA_IMG_NAME="zosia_prod_web:${TAG}"
ZOSIA_IMG_ID=`docker images ${ZOSIA_IMG_NAME} | tail -1 | awk '{ print $3 }'`

DOCKER_REPO_URI="${DOCKER_REPO_URI_BASE}/zosia_web"
REGISTRY_IMG_NAME="${DOCKER_REPO_URI}:${TAG}"
docker tag ${ZOSIA_IMG_ID} ${REGISTRY_IMG_NAME}
docker push ${REGISTRY_IMG_NAME}

# upload zosia_nginx image
NGINX_IMG_NAME="zosia_prod_nginx:${TAG}"
NGINX_IMG_ID=`docker images ${NGINX_IMG_NAME} | tail -1 | awk '{ print $3 }'`

DOCKER_REPO_URI="${DOCKER_REPO_URI_BASE}/zosia_nginx"
REGISTRY_IMG_NAME="${DOCKER_REPO_URI}:${TAG}"
docker tag ${NGINX_IMG_ID} ${REGISTRY_IMG_NAME}
docker push ${REGISTRY_IMG_NAME}
