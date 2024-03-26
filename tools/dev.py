#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse as argp
from os.path import dirname, normpath
import subprocess as subp


class Colour:
    BLUE = "\033[1;34m"
    PURPLE = "\033[1;35m"
    YELLOW = "\033[1;33m"
    WHITE = "\033[1;37m"
    NORMAL = "\033[0m"


PROJECT_NAME = "zosia"
ROOT_DIR = normpath(dirname(__file__) + "/..")
DOCKER_COMPOSE = f"{ROOT_DIR}/docker-compose.dev.yml"

WEB_CONTAINER_NAME = f"{PROJECT_NAME}_web_1"
DB_CONTAINER_NAME = f"{PROJECT_NAME}_db_1"

FILE_SYSTEM_NOTE = f"[{Colour.YELLOW}note:{Colour.NORMAL} this may create files on host fs with " \
                   f"root permissions]"
SUBCOMMANDS_NOTE = "[contains subcommands]"


def command_run(command):
    if args.debug:
        print(
            f"{Colour.WHITE}** {Colour.YELLOW}{subp.list2cmdline(command)}{Colour.WHITE} **"
            f"{Colour.NORMAL}")

    proc = subp.run(command, check=False)
    return proc.returncode


def docker_exec(command, container):
    command_run(["docker", "exec", "-it", container] + command)


def docker_shell(command):
    docker_exec(["/bin/bash", "-c", subp.list2cmdline(command)], WEB_CONTAINER_NAME)


def docker_python(command):
    docker_shell(["python", "src/manage.py"] + command)


def docker_compose_run(command, with_project=True):
    project = ["-p", PROJECT_NAME] if with_project else []
    status_code = command_run(
        ["docker", "compose", "--compatibility", "-f", DOCKER_COMPOSE] + project + command)
    if status_code != 0:
        exit(1)


def web_install():
    docker_shell(["yarn", "install"])


def web_build():
    docker_shell(["yarn", "build"])


def run_server():
    docker_python(["runserver", "0.0.0.0:8000"])
    print(
        f"{Colour.PURPLE}-- Exiting --{Colour.NORMAL}",
        f"{Colour.YELLOW} [!] Remember to run `dev.py quit`, if you've just finished"
        f"{Colour.NORMAL}",
        sep="\n")
    command_run(["docker", "ps"])


def setup(is_no_cache):
    no_cache_opt = ["--no-cache"] if is_no_cache else []
    docker_compose_run(["build"] + no_cache_opt, with_project=False)
    docker_compose_run(["up", "-d"])
    web_install()
    web_build()


def migrate(is_create_admin, is_create_data):
    docker_python(["migrate"])

    if is_create_admin:
        print(f"{Colour.PURPLE}-- Set password for super user account --{Colour.NORMAL}")
        docker_python(["createsuperuser", "--email", "admin@zosia.org", "--first_name", "Admin",
                       "--last_name", "Zosiowicz"])

    if is_create_data:
        print(f"{Colour.PURPLE}-- Prepare some random data --{Colour.NORMAL}")
        docker_python(["create_data"])


parser = argp.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true", help="print commands before execution")
subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

one_click_parser = subparsers.add_parser("run", aliases=["r"],
                                         help="build containers and run zosia website (localhost, "
                                              "port 8000)")
one_click_parser.add_argument("--create-admin", action="store_true",
                              help="create super user account (password specified manually)")
one_click_parser.add_argument("--create-data", action="store_true",
                              help="create some random data to work on, like conference, buses, "
                                   "rooms, etc.")
one_click_parser.add_argument("--no-cache", action="store_true",
                              help="do not use cache when building container images")

setup_parser = subparsers.add_parser("start", aliases=["setup", "s"],
                                     help="spin up containers and prepare development environment")
setup_parser.add_argument("--no-cache", action="store_true",
                          help="do not use cache when building the container image")

shutdown_parser = subparsers.add_parser("quit", aliases=["shutdown", "q"],
                                        help="kill and destroy containers")

test_parser = subparsers.add_parser("test", aliases=["t"],
                                    help="run Django tests inside the container")
test_parser.add_argument("-v", "--verbose", action="store_true",
                         help="add verbose option to test command")

shell_parser = subparsers.add_parser("shell", aliases=["sh"],
                                     help=f"run shell inside a container {SUBCOMMANDS_NOTE}")

shell_subparsers = shell_parser.add_subparsers(dest="shell", metavar="SHELL", required=True)

shell_subparsers.add_parser("bash", add_help=False, help="run Bash shell in website container")
shell_subparsers.add_parser("postgres", aliases=["psql"], add_help=False,
                            help="run Postgres shell (psql) in database container")

migrate_parser = subparsers.add_parser("migrations", aliases=["m"],
                                       help=f"operate on Django migrations {SUBCOMMANDS_NOTE}")

migrate_subparsers = migrate_parser.add_subparsers(dest="action", metavar="ACTION", required=True)

migr_apply_parser = migrate_subparsers.add_parser("apply", aliases=["a"],
                                                  help="apply Django database migrations")
migr_apply_parser.add_argument("--create-admin", action="store_true",
                               help="create super user account (password specified manually)")
migr_apply_parser.add_argument("--create-data", action="store_true",
                               help="create some random data to work on like conference, buses, "
                                    "rooms, etc.")
migrate_subparsers.add_parser("make", aliases=["m"], add_help=False,
                              help=f"generate Django migrations from models {FILE_SYSTEM_NOTE}")

run_server_parser = subparsers.add_parser(
    "server", aliases=["sv"],
    help="run Django development server inside the container (localhost, port 8000)")

web_parser = subparsers.add_parser(
    "web", aliases=["javascript", "js"],
    help=f"perform action related to web application {SUBCOMMANDS_NOTE}")

web_subparsers = web_parser.add_subparsers(dest="action", metavar="ACTION", required=True)

web_subparsers.add_parser("install", aliases=["i"], add_help=False,
                          help="install web app's dependencies from file `package.json`")
web_subparsers.add_parser("build", aliases=["b"], add_help=False,
                          help=f"build web app {FILE_SYSTEM_NOTE}")
web_subparsers.add_parser("watch", aliases=["w"], add_help=False,
                          help=f"rebuild web app on file change {FILE_SYSTEM_NOTE}")

py_parser = subparsers.add_parser("python", aliases=["py"],
                                  help=f"perform action related to Python language "
                                       f"{SUBCOMMANDS_NOTE}")

py_subparsers = py_parser.add_subparsers(dest="action", metavar="ACTION", required=True)

py_subparsers.add_parser("install", aliases=["i"], add_help=False,
                         help="install Python dependencies from file `requirements.txt`")
py_subparsers.add_parser("upgrade", aliases=["u"], add_help=False,
                         help="upgrade Python dependencies from file `requirements.txt`")
py_subparsers.add_parser("pip", add_help=False, help="upgrade pip")

args = parser.parse_args()

if args.command in ["run", "r"]:
    print(f"{Colour.BLUE}-- Setup container --{Colour.NORMAL}")
    setup(args.no_cache)
    print(f"{Colour.BLUE}-- Run migrations --{Colour.NORMAL}")
    migrate(args.create_admin, args.create_data)
    print(f"{Colour.BLUE}-- Run webserver --{Colour.NORMAL}")
    run_server()
elif args.command in ["start", "setup", "s"]:
    setup(args.no_cache)
elif args.command in ["quit", "shutdown", "q"]:
    docker_compose_run(["down"])
elif args.command in ["test", "t"]:
    docker_python(["test"] + (["-v", "2"] if args.verbose else []))
elif args.command in ["shell", "sh"]:
    if args.shell in ["bash"]:
        docker_exec(["/bin/bash"], WEB_CONTAINER_NAME)
    elif args.shell in ["postgres", "psql"]:
        docker_exec(["psql", "-U", "zosia"], DB_CONTAINER_NAME)
    else:
        shell_parser.print_help()
elif args.command in ["migrations", "m"]:
    if args.action in ["apply", "a"]:
        migrate(args.create_admin, args.create_data)
    elif args.action in ["make", "m"]:
        docker_python(["makemigrations"])
    else:
        migrate_parser.print_help()
elif args.command in ["server", "sv"]:
    run_server()
elif args.command in ["web", "javascript", "js"]:
    if args.action in ["install", "i"]:
        web_install()
    elif args.action in ["build", "b"]:
        web_build()
    elif args.action in ["watch", "w"]:
        docker_shell(["yarn", "watch"])
    else:
        web_parser.print_help()
elif args.command in ["python", "py"]:
    if args.action in ["install", "i"]:
        docker_shell(["pip", "install", "-r", "requirements.txt"])
    elif args.action in ["upgrade", "u"]:
        docker_shell(["pip", "install", "-U", "-r", "requirements.txt"])
    elif args.action in ["pip"]:
        docker_shell(["pip", "install", "-U", "pip"])
    else:
        py_parser.print_help()
else:
    parser.print_help()
