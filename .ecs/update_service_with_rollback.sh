#!/bin/bash
CLUSTER_NAME="zosia-cluster"
SERVICE_NAME="zosia-site-v2"
TASK_DEF="zosia-site"

function update_service () {
    local task_def=${1};

    aws ecs update-service --region ${AWS_DEFAULT_REGION} --cluster ${CLUSTER_NAME} --service ${SERVICE_NAME} --task-definition ${task_def} > /dev/null;
    return $?
}

echo "Updating service ${SERVICE_NAME} in ${CLUSTER_NAME}."

current_task_definition=$(aws ecs describe-services --region ${AWS_DEFAULT_REGION} --cluster ${CLUSTER_NAME} --services ${SERVICE_NAME} | jq -c -r ".services[0].taskDefinition")

# TODO: Wait for deployment to finish
if ! update_service ${TASK_DEF};
then
    echo "ERROR: Update service ${SERVICE_NAME} failure, ROLLBACK!"
    update_service ${current_task_definition}
    exit -1
fi
