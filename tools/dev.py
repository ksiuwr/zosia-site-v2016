#! /usr/bin/python3
# -*- coding: utf-8 -*-

import argparse as argp
from os.path import dirname, normpath
from shlex import quote
import subprocess as subp

C_blue = ""
C_green = ""
C_purple = ""
C_yellow = ""
C_bold = ""
C_normal = ""

PROJECT_NAME = "zosia"
ROOT_DIR = normpath(dirname(__file__) + "/..")
DOCKER_COMPOSE = f"{ROOT_DIR}/docker-compose.dev.yml"
WEB_CONTAINER_NAME = f"{PROJECT_NAME}_web_1"
DB_CONTAINER_NAME = f"{PROJECT_NAME}_db_1"


def shell_run(command):
    if args.debug:
        print(f"** {C_bold}{C_yellow}{command}{C_normal} **")

    subp.run(command, shell=True)


def docker_exec(command, container):
    shell_run(f"docker exec -it {container} {command}")


def docker_shell(command):
    docker_exec(f"/bin/bash -c {quote(command)}", WEB_CONTAINER_NAME)


def docker_python(command):
    docker_shell(f"python src/manage.py {command}")


def docker_compose(command, with_project=True):
    project = f"-p {PROJECT_NAME}" if with_project else ""
    shell_run(f"docker-compose -f {quote(DOCKER_COMPOSE)} {project} {command}")


def setup():
    docker_compose(f"build {args.no_cache}", with_project=False)
    docker_compose("up -d")
    js_install()
    js_build()


def js_install():
    docker_shell("yarn install")


def js_build():
    docker_shell("yarn build")


def run_server():
    docker_python("runserver 0.0.0.0:8000")
    print(
        f"{C_bold}{C_purple}-- Exiting --{C_normal}",
        f"{C_bold}{C_blue}* Remember to run `./dev.py shutdown`, if you've just finished{C_normal}",
        sep="\n")
    shell_run("docker ps")


def migrate():
    docker_python("migrate")

    if args.create_admin:
        print(f"{C_bold}{C_purple}-- Set password for super user account --{C_normal}")
        docker_python(
            "createsuperuser --email admin@zosia.org --first_name Admin --last_name Zosiowicz")

    if args.create_data:
        print(f"{C_bold}{C_purple}-- Prepare some random data --{C_normal}")
        docker_python("create_data")


parser = argp.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true")
subparsers = parser.add_subparsers(title="command", dest="command")

one_click_parser = subparsers.add_parser("one_click")
one_click_parser.add_argument("--create-admin", action="store_true")
one_click_parser.add_argument("--create-data", action="store_true")
one_click_parser.add_argument("--no-cache", action="store_const", const="--no_cache", default="")

setup_parser = subparsers.add_parser("setup")
setup_parser.add_argument("--no-cache", action="store_const", const="--no_cache", default="")

shutdown_parser = subparsers.add_parser("shutdown")

test_parser = subparsers.add_parser("test")

shell_parser = subparsers.add_parser("shell")
shell_parser.add_argument("type", type=str, choices=("bash", "postgres"))

make_migrations_parser = subparsers.add_parser("make_migrations")

migrate_parser = subparsers.add_parser("migrate")
migrate_parser.add_argument("--create-admin", action="store_true")
migrate_parser.add_argument("--create-data", action="store_true")

run_server_parser = subparsers.add_parser("run_server")

js_parser = subparsers.add_parser("js")
js_parser.add_argument("action", type=str, choices=("install", "build", "watch"))

py_parser = subparsers.add_parser("python")
py_parser.add_argument("action", type=str, choices=("install",))

args = parser.parse_args()

if args.command == "one_click":
    print(f"{C_bold}{C_blue}-- Setup container --${C_normal}")
    setup()
    print(f"{C_bold}{C_blue}-- Run migrations --{C_normal}")
    migrate()
    print(f"{C_bold}{C_blue}-- Run webserver --{C_normal}")
    run_server()
elif args.command == "setup":
    setup()
elif args.command == "shutdown":
    docker_compose("down")
elif args.command == "test":
    docker_python("test")
elif args.command == "shell":
    if args.type == "bash":
        docker_exec("/bin/bash", WEB_CONTAINER_NAME)
    elif args.type == "postgres":
        docker_exec("psql -U zosia", DB_CONTAINER_NAME)
elif args.command == "make_migrations":
    docker_python("makemigrations")
elif args.command == "migrate":
    migrate()
elif args.command == "run_server":
    run_server()
elif args.command == "js":
    if args.action == "install":
        js_install()
    elif args.action == "build":
        js_build()
    elif args.action == "watch":
        docker_shell("yarn watch")
elif args.command == "python":
    if args.action == "install":
        docker_shell("pip install -r requirements.txt")
