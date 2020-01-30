# -*- coding: utf-8 -*-
import argparse as argp
from shlex import quote
import subprocess as subp


def bash():
    subp.run(f"docker exec -it {WEB_CONTAINER_NAME} /bin/bash", shell=True)


def psql():
    subp.run(f"docker exec -it {quote(DB_CONTAINER_NAME)} psql -U zosia", shell=True)


def shutdown():
    subp.run(f"docker-compose -f {quote(DOCKER_COMPOSE)} -p {quote(PROJECT_NAME)} down", shell=True)


parser = argp.ArgumentParser()
subparsers = parser.add_subparsers("command")

one_click_parser = subparsers.add_parser("one_click")
one_click_parser.add_argument("--create-admin")
one_click_parser.add_argument("--create-data")
one_click_parser.add_argument("--no-cache")

setup_parser = subparsers.add_parser("setup")
setup_parser.add_argument("--no-cache")

shutdown_parser = subparsers.add_parser("shutdown")

test_parser = subparsers.add_parser("test")

shell_parser = subparsers.add_parser("shell")
shell_parser.add_argument("type", type=str, choices=("bash", "postgres"))

make_migrations_parser = subparsers.add_parser("make_migrations")

migrate_parser = subparsers.add_parser("migrate")
migrate_parser.add_argument("--create-admin")
migrate_parser.add_argument("--create-data")

run_server_parser = subparsers.add_parser("run_server")

js_parser = subparsers.add_parser("js")
js_parser.add_argument("action", type=str, choices=("install", "build", "watch"))

py_parser = subparsers.add_parser("python")
py_parser.add_argument("action", type=str, choices=("install",))

parser.parse_args()
