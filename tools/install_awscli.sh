#!/usr/bin/env bash

HELP_TEXT="Install (or upgrade) AWS CLI tool.

Usage:
    ./install_awscli.sh [options]

Options:
    --upgrade   - upgrade the awscli package
    --help      - prints this help message
"

UPGRADE=0

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --help)
    echo "${HELP_TEXT}"
    exit 0
    ;;
    --upgrade)
    UPGRADE=1
    shift
    ;;
    *)
    echo "Argument $1 is not supported."
    echo "${HELP_TEXT}"
    exit 1
    ;;
esac
done

which aws &> /dev/null
AWSCLI_INSTALLED="$?"

if [[ ${AWSCLI_INSTALLED} -eq 1 ]] || [[ ${UPGRADE} -eq 1 ]]; then
    sudo pip install --upgrade --user awscli
fi

aws configure --profile zosia
