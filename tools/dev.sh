#!/bin/bash

HELP_TEXT="Run the zosia docker containers for local development.
Usage:
    ./dev.sh [command]

Commands
  one_click       - Runs zosia website (on 127.0.0.1:8000)
  setup           - Spins up the containers and prepares development enviromanet
  runserver       - Runs django development server inside of container 
  py_install      - Installs python dependencies specified in requirements.txt
  js_install      - Installs javascript depedencies specified in package.json
  js_watch        - Rebuilds javascript on file change (note: may create files on host fs with root permissions)
  js_build        - Builds javascript (note: may create files on host fs with root permissions)
  migrate         - Applies migrations of django application
  makemigrations  - Generates django migrations from models (note: may create files on host fs with root permissions)
  shutdown        - Kills and deletes containers
"

function configure_env () {
  local cwd=$(pwd)
  cd $(dirname "$0")
  SCRIPT_PATH=$(pwd)
  cd ../
  ROOT_PATH=$(pwd)
  cd "$cwd"
  DOCKER_COMPOSE="$ROOT_PATH/docker-compose.dev.yml"
  WEB_CONTAINER_NAME=$(basename $cwd)"_web_1"
}

configure_env


function build() {
  docker-compose -f $DOCKER_COMPOSE build
}

function run() {
  docker exec -it $WEB_CONTAINER_NAME /bin/bash -c "$1"
}

function js_install () {
  run "yarn install"
}

function js_watch () {
  run "yarn watch"
}

function js_build () {
  run "yarn build"
}

function py_install () {
  run "pip install -r requirements.txt"
}

function makemigrations() {
  run "python src/manage.py makemigrations"
}

function migrate () {
  run "python src/manage.py migrate"
}

function runserver () {
  run "python src/manage.py runserver 0.0.0.0:8000"
}

function setup () {
  build
  docker-compose -f docker-compose.dev.yml up -d
  js_install
  js_build
  py_install
}

function shutdown () {
  docker-compose -f docker-compose.dev.yml down
}

function one_click () {
  setup
  migrate
  runserver
}

command="$1"
shift

case $command in
  one_click)
  one_click
  ;;
  setup)
  setup
  ;;
  runserver)
  runserver
  ;;
  py_install)
  py_install
  ;;
  run)
  run "$2"
  ;;
  js_watch)
  js_watch
  ;;
  js_build)
  js_build
  ;;
  js_install)
  js_install
  ;;
  shutdown)
  shutdown
  ;;
  migrate)
  migrate
  ;;
  makemigrations)
  makemigrations
  ;;
esac
