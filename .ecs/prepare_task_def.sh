#!/bin/sh

# Prepare new task definition
task_file=".ecs/task_def.json"

sed \
    -e "s|__AWS_DEFAULT_REGION__|${AWS_DEFAULT_REGION}|g" \
    -e "s|__VERSION__|${VERSION_TAG}|g" \
    -e "s|__AWS_ACCOUNT_ID__|${AWS_ACCOUNT_ID}|g" \
    ${task_file} > ${task_file}.new;

aws ecs register-task-definition --region ${AWS_DEFAULT_REGION} --cli-input-json file://${task_file}.new >/dev/null;
rm ${task_file}.new;