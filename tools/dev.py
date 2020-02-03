#! /usr/bin/python3
# -*- coding: utf-8 -*-

import argparse as argp
from os.path import dirname, normpath
from shlex import quote
import subprocess as subp

C_blue = "\033[1;34m"
C_purple = "\033[1;35m"
C_yellow = "\033[1;33m"
C_white = "\033[1;37m"
C_normal = "\033[0m"

PROJECT_NAME = "zosia"
ROOT_DIR = normpath(dirname(__file__) + "/..")
DOCKER_COMPOSE = f"{ROOT_DIR}/docker-compose.dev.yml"
WEB_CONTAINER_NAME = f"{PROJECT_NAME}_web_1"
DB_CONTAINER_NAME = f"{PROJECT_NAME}_db_1"
FILE_SYSTEM_NOTE = f"({C_yellow}note:{C_normal} this may create files on host fs with root permissions)"


def shell_run(command):
    if args.debug:
        print(f"{C_white}** {C_yellow}{command}{C_white} **{C_normal}")

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


def setup(is_no_cache):
    no_cache_opt = "--no-cache" if is_no_cache else ""
    docker_compose(f"build {no_cache_opt}", with_project=False)
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
        f"{C_purple}-- Exiting --{C_normal}",
        f"{C_yellow} [!] Remember to run `./dev.py shutdown`, if you've just finished{C_normal}",
        sep="\n")
    shell_run("docker ps")


def migrate(is_create_admin, is_create_data):
    docker_python("migrate")

    if is_create_admin:
        print(f"{C_purple}-- Set password for super user account --{C_normal}")
        docker_python(
            "createsuperuser --email admin@zosia.org --first_name Admin --last_name Zosiowicz")

    if is_create_data:
        print(f"{C_purple}-- Prepare some random data --{C_normal}")
        docker_python("create_data")


parser = argp.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true", help="print commands before execution")
subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

one_click_parser = subparsers.add_parser("one_click", aliases=["x"],
                                         help="run zosia website (localhost, port 8000)")
one_click_parser.add_argument("--create-admin", action="store_true",
                              help="create super user account (password specified manually)")
one_click_parser.add_argument("--create-data", action="store_true",
                              help="create some random data to work on like conference, buses, rooms, etc.")
one_click_parser.add_argument("--no-cache", action="store_const", const="--no_cache", default="",
                              help="do not use cache when building the container image")

setup_parser = subparsers.add_parser("setup", aliases=["s"],
                                     help="spin up the containers and prepare development enviroment")
setup_parser.add_argument("--no-cache", action="store_true",
                          help="Do not use cache when building the container image")

shutdown_parser = subparsers.add_parser("shutdown", aliases=["q"],
                                        help="kill and destroy containers")

test_parser = subparsers.add_parser("test", aliases=["t"],
                                    help="run Django tests inside the container")

shell_parser = subparsers.add_parser("shell", aliases=["sh"], help="run shell inside a container")
shell_subparsers = shell_parser.add_subparsers(dest="shell", metavar="SHELL", required=True)
shell_subparsers.add_parser("bash", add_help=False, help="run Bash shell in website container")
shell_subparsers.add_parser("postgres", aliases=["psql"], add_help=False,
                            help="run Postgres shell (psql) in database container")

make_migrations_parser = subparsers.add_parser("make_migrations", aliases=["mm"],
                                               help=f"generate Django migrations from models {FILE_SYSTEM_NOTE}")

migrate_parser = subparsers.add_parser("migrate", aliases=["m"],
                                       help="apply Django database migrations")
migrate_parser.add_argument("--create-admin", action="store_true",
                            help="create super user account (password specified manually)")
migrate_parser.add_argument("--create-data", action="store_true",
                            help="create some random data to work on like conference, buses, rooms, etc.")

run_server_parser = subparsers.add_parser("run_server", aliases=["rs"],
                                          help="run Django development server inside the container")

js_parser = subparsers.add_parser("javascript", aliases=["js"],
                                  help="perform action related to JavaScript language")
js_subparsers = js_parser.add_subparsers(dest="action", metavar="ACTION", required=True)
js_subparsers.add_parser("install", aliases=["i"], add_help=False,
                         help="install JavaScript depedencies from file package.json")
js_subparsers.add_parser("build", aliases=["b"], add_help=False,
                         help=f"build JavaScript {FILE_SYSTEM_NOTE}")
js_subparsers.add_parser("watch", aliases=["w"], add_help=False,
                         help=f"rebuild JavaScript on file change {FILE_SYSTEM_NOTE}")

py_parser = subparsers.add_parser("python", aliases=["py"],
                                  help="perform action related to Python language")
py_subparsers = py_parser.add_subparsers(dest="action", metavar="ACTION", required=True)
py_subparsers.add_parser("install", aliases=["i"], add_help=False,
                         help="install Python dependencies from file requirements.txt")

args = parser.parse_args()

if args.command in ["one_click", "x"]:
    print(f"{C_blue}-- Setup container --{C_normal}")
    setup(args.no_cache)
    print(f"{C_blue}-- Run migrations --{C_normal}")
    migrate(args.create_admin, args.create_data)
    print(f"{C_blue}-- Run webserver --{C_normal}")
    run_server()
elif args.command in ["setup", "s"]:
    setup(args.no_cache)
elif args.command in ["shutdown", "q"]:
    docker_compose("down")
elif args.command in ["test", "t"]:
    docker_python("test")
elif args.command in ["shell", "sh"]:
    if args.shell == "bash":
        docker_exec("/bin/bash", WEB_CONTAINER_NAME)
    elif args.shell in ["postgres", "psql"]:
        docker_exec("psql -U zosia", DB_CONTAINER_NAME)
elif args.command in ["make_migrations", "mm"]:
    docker_python("makemigrations")
elif args.command in ["migrate", "m"]:
    migrate(args.create_admin, args.create_data)
elif args.command in ["run_server", "rs"]:
    run_server()
elif args.command in ["javascript", "js"]:
    if args.action in ["install", "i"]:
        js_install()
    elif args.action in ["build", "b"]:
        js_build()
    elif args.action in ["watch", "w"]:
        docker_shell("yarn watch")
elif args.command in ["python", "py"]:
    if args.action in ["install", "i"]:
        docker_shell("pip install -r requirements.txt")
else:
    parser.print_help()
