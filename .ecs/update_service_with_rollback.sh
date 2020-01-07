#!/bin/bash

CLUSTER_NAME="zosia-cluster"
SERVICE_NAME="zosia-site-v2"
TASK_DEF="zosia-site"

function update_service () {
    local task_def=${1};

    aws ecs update-service --region ${AWS_DEFAULT_REGION} --cluster ${CLUSTER_NAME} --service ${SERVICE_NAME} --task-definition ${task_def} > /dev/null;
    return $?
}

function wait_for_service () {
    echo "Waiting for service to become stable..."
    aws ecs wait services-stable --region ${AWS_DEFAULT_REGION} --cluster ${CLUSTER_NAME} --services ${SERVICE_NAME}
    return $?
}

echo "Updating service ${SERVICE_NAME} in ${CLUSTER_NAME}."

current_task_definition=$(aws ecs describe-services --region ${AWS_DEFAULT_REGION} --cluster ${CLUSTER_NAME} --services ${SERVICE_NAME} | jq -c -r ".services[0].taskDefinition")

if ! update_service ${TASK_DEF} || ! wait_for_service ;
then
    echo "ERROR: Fail to update service ${SERVICE_NAME}, ROLLBACK!"
    update_service ${current_task_definition}
    exit -1
fi

echo "Done"
