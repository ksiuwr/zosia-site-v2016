#!/bin/sh
set -eu

: '
This script is used by CircleCI to upload image to ECR during CICD process.
Please remember about setting proper repository URL and AWS region.
'

# Configuration
DOCKER_REPO_URI_BASE="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
ZOSIA_IMG_NAME="zosia_prod_web"
TAG="${VERSION_TAG}"

# Login and upload images
echo "Logging to remote registry with command"
aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
    docker login --username AWS --password-stdin $DOCKER_REPO_URI_BASE

# upload zosia_web image
ZOSIA_IMG_ID=$(docker images ${ZOSIA_IMG_NAME}:latest | tail -1 | awk '{ print $3 }')

DOCKER_REPO_URI="${DOCKER_REPO_URI_BASE}/zosia_web"
REGISTRY_IMG_NAME="${DOCKER_REPO_URI}:${TAG}"
docker tag ${ZOSIA_IMG_ID} ${REGISTRY_IMG_NAME}
docker push ${REGISTRY_IMG_NAME}
