#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse as argp
from os.path import dirname, normpath
import subprocess as subp
from typing import List, Optional


class Colour:
    BLUE = "\033[1;34m"
    PURPLE = "\033[1;35m"
    YELLOW = "\033[1;33m"
    WHITE = "\033[1;37m"
    NORMAL = "\033[0m"


PROJECT_NAME = "zosia"
ROOT_DIR = normpath(f"{dirname(__file__)}/..")
DOCKER_COMPOSE = f"{ROOT_DIR}/docker-compose.dev.yml"

WEB_CONTAINER_NAME = f"{PROJECT_NAME}_web_1"
DB_CONTAINER_NAME = f"{PROJECT_NAME}_db_1"

FILE_SYSTEM_NOTE = (
    f"[{Colour.YELLOW}note:{Colour.NORMAL}"
    f" this may create files on host file system with root permissions]")
SUBCOMMANDS_NOTE = "[contains subcommands]"
DEBUG_MODE = False


def command_run(command: List[str]) -> int:
    if DEBUG_MODE:
        print(
            f"{Colour.WHITE}** {Colour.YELLOW}{subp.list2cmdline(command)}"
            f"{Colour.WHITE} **{Colour.NORMAL}")

    proc = subp.run(command, check=False)
    return proc.returncode


def remind_quit() -> None:
    print(
        f"{Colour.YELLOW} [!] Remember to run `dev.py quit`, "
        f"if you want to stop running containers"
        f"{Colour.NORMAL}",
        sep="\n")
    command_run(["docker", "ps"])


def docker_exec(command: List[str], container: str) -> None:
    command_run(["docker", "exec", "-it", container] + command)


def docker_shell(command: List[str]) -> None:
    docker_exec(["/bin/bash", "-c", subp.list2cmdline(command)], WEB_CONTAINER_NAME)


def docker_python(command: List[str]) -> None:
    docker_shell(["python", "src/manage.py"] + command)


def docker_compose_run(command: List[str], with_project: bool = True) -> None:
    project = ["-p", PROJECT_NAME] if with_project else []
    status_code = command_run(
        ["docker", "compose", "--compatibility", "-f", DOCKER_COMPOSE] + project + command)
    if status_code != 0:
        exit(1)


def web_install() -> None:
    docker_shell(["yarn", "install"])


def web_build() -> None:
    docker_shell(["yarn", "build"])


def setup(is_no_cache: bool, display_remind: bool = False) -> None:
    no_cache_opt = ["--no-cache"] if is_no_cache else []
    docker_compose_run(["build"] + no_cache_opt, with_project=False)
    docker_compose_run(["up", "-d"])
    web_install()
    web_build()

    if display_remind:
        remind_quit()


def shutdown():
    docker_compose_run(["down"])


def run_server(display_remind: bool = False) -> None:
    docker_python(["runserver", "0.0.0.0:8000"])
    print(f"{Colour.PURPLE}-- Exiting server --{Colour.NORMAL}")

    if display_remind:
        remind_quit()


def run_tests(modules: Optional[List[str]], is_verbose: bool):
    command = ["test"]

    if modules:
        command += list(modules)

    if is_verbose:
        command += ["-v", "2"]

    docker_python(command)


def migrate(is_create_admin: bool, is_create_data: bool) -> None:
    docker_python(["migrate"])

    if is_create_admin:
        print(f"{Colour.PURPLE}-- Set password for super user account --"
              f"{Colour.NORMAL}")
        docker_python(["createsuperuser", "--email", "admin@zosia.org",
                       "--first_name", "Admin",
                       "--last_name", "Zosiowicz"])

    if is_create_data:
        print(f"{Colour.PURPLE}-- Prepare some random data --{Colour.NORMAL}")
        docker_python(["create_data"])


def cli():
    parser = argp.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true",
                        help="print commands before execution")
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    run_app_parser = subparsers.add_parser(
        "run-app", aliases=["r", "run", "app"],
        help="build containers and run zosia website (localhost, port 8000)")
    run_app_parser.add_argument(
        "-A", "--create-admin", action="store_true",
        help="create super user account (password specified manually)")
    run_app_parser.add_argument(
        "-D", "--create-data", action="store_true",
        help="create some random data to work on, like conference, transport, rooms, etc.")
    run_app_parser.add_argument(
        "--no-cache", action="store_true",
        help="do not use cache when building container images")
    run_app_parser.add_argument(
        "-k", "--keep-alive", action="store_true",
        help="keep containers running after exiting server")

    start_parser = subparsers.add_parser(
        "start", aliases=["setup", "s"],
        help="spin up containers and prepare development environment")
    start_parser.add_argument(
        "--no-cache", action="store_true",
        help="do not use cache when building the container image")

    quit_parser = subparsers.add_parser(
        "quit", aliases=["shutdown", "q"], help="kill and destroy containers")

    test_parser = subparsers.add_parser(
        "test", aliases=["t"],
        help="run Django tests inside the container")
    test_parser.add_argument(
        "-M", "--module", action="append",
        help="module or directory to run tests from [option can be repeated]")
    test_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="add verbose option to test command")

    run_test_parser = subparsers.add_parser(
        "run-test", aliases=["rt"],
        help="build containers and run Django tests")
    run_test_parser.add_argument(
        "-M", "--module", action="append",
        help="module or directory to run tests from [option can be repeated]")
    run_test_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="add verbose option to test command")

    bash_parser = subparsers.add_parser(
        "bash", aliases=["shell", "sh"],
        help=f"run Bash shell inside website container")

    postgres_parser = subparsers.add_parser(
        "postgres", aliases=["psql"], add_help=False,
        help="run Postgres shell (psql) in database container")

    migrations_parser = subparsers.add_parser(
        "migrations", aliases=["m"],
        help=f"operate on Django migrations {SUBCOMMANDS_NOTE}")

    migrations_subparsers = migrations_parser.add_subparsers(
        dest="action", metavar="ACTION", required=True)

    migrations_apply_parser = migrations_subparsers.add_parser(
        "apply", aliases=["a"],
        help="apply Django database migrations")
    migrations_apply_parser.add_argument(
        "-A", "--create-admin", action="store_true",
        help="create super user account (password specified manually)")
    migrations_apply_parser.add_argument(
        "-D", "--create-data", action="store_true",
        help="create some random data to work on like conference, transport, rooms, etc.")
    migrations_subparsers.add_parser(
        "make", aliases=["m"], add_help=False,
        help=f"generate Django migrations from models {FILE_SYSTEM_NOTE}")

    serve_parser = subparsers.add_parser(
        "serve", aliases=["server", "sv"],
        help="run Django development server inside the container "
             "(localhost, port 8000, http://localhost:8000/)")

    web_parser = subparsers.add_parser(
        "web", aliases=["javascript", "js"],
        help=f"perform action related to web application {SUBCOMMANDS_NOTE}")

    web_subparsers = web_parser.add_subparsers(
        dest="action", metavar="ACTION", required=True)

    web_subparsers.add_parser(
        "install", aliases=["i"], add_help=False,
        help="install web app's dependencies from file `package.json`")
    web_subparsers.add_parser(
        "build", aliases=["b"], add_help=False,
        help=f"build web app {FILE_SYSTEM_NOTE}")
    web_subparsers.add_parser(
        "watch", aliases=["w"], add_help=False,
        help=f"rebuild web app on file change {FILE_SYSTEM_NOTE}")

    python_parser = subparsers.add_parser(
        "python", aliases=["py"],
        help=f"perform action related to Python language {SUBCOMMANDS_NOTE}")

    python_subparsers = python_parser.add_subparsers(
        dest="action", metavar="ACTION", required=True)

    python_subparsers.add_parser(
        "install", aliases=["i"], add_help=False,
        help="install Python dependencies from file `requirements.txt`")
    python_subparsers.add_parser(
        "upgrade", aliases=["u"], add_help=False,
        help="upgrade Python dependencies from file `requirements.txt`")
    python_subparsers.add_parser(
        "pip", add_help=False, help="upgrade pip")

    args = parser.parse_args()

    global DEBUG_MODE  # pylint: disable=W0603
    DEBUG_MODE = args.debug

    if args.command in ["run-app", "r", "run", "app"]:
        print(f"{Colour.BLUE}-- Setup containers --{Colour.NORMAL}")
        setup(args.no_cache)
        print(f"{Colour.BLUE}-- Run migrations --{Colour.NORMAL}")
        migrate(args.create_admin, args.create_data)
        print(f"{Colour.BLUE}-- Run webserver --{Colour.NORMAL}")
        run_server(args.keep_alive)

        if not args.keep_alive:
            print(f"{Colour.BLUE}-- Quit containers --{Colour.NORMAL}")
            shutdown()

    elif args.command in ["run-test", "rt"]:
        print(f"{Colour.BLUE}-- Setup containers --{Colour.NORMAL}")
        setup(False)
        print(f"{Colour.BLUE}-- Run tests --{Colour.NORMAL}")
        run_tests(args.module, args.verbose)
        print(f"{Colour.BLUE}-- Quit containers --{Colour.NORMAL}")
        shutdown()

    elif args.command in ["start", "setup", "s"]:
        setup(args.no_cache, True)

    elif args.command in ["quit", "shutdown", "q"]:
        shutdown()

    elif args.command in ["test", "t"]:
        run_tests(args.module, args.verbose)

    elif args.command in ["bash", "shell", "sh"]:
        docker_exec(["/bin/bash"], WEB_CONTAINER_NAME)

    elif args.command in ["postgres", "psql"]:
        docker_exec(["psql", "-U", "zosia"], DB_CONTAINER_NAME)

    elif args.command in ["migrations", "m"]:
        if args.action in ["apply", "a"]:
            migrate(args.create_admin, args.create_data)
        elif args.action in ["make", "m"]:
            docker_python(["makemigrations"])
        else:
            migrations_parser.print_help()

    elif args.command in ["server", "serve", "sv"]:
        run_server(True)

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
            python_parser.print_help()

    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
