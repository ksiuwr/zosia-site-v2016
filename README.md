# zosia-site-v2016

Django 3.2 version of ZOSIA registration page.

[![CircleCI](https://circleci.com/gh/ksiuwr/zosia-site-v2016/tree/master.svg?style=svg)](https://circleci.com/gh/ksiuwr/zosia-site-v2016/tree/master)

- [Development](#development)
    - [Full in-docker local development](#full-in-docker-local-development)
        - [Required software](#required-software)
        - [How can I run it?](#how-can-i-run-it)
        - [I have run it - what is happening?](#i-have-run-it---what-is-happening)
    - [Troubleshooting](#troubleshooting)
- [Hosting](#hosting)

## Development

The preferred approach is to use _docker_ for development. And don't worry, we try to keep it as
easy as possible. Of course, if you're really not into containerisation, you can try running it
without docker, but you may find it harder to debug OS related bugs. Besides, on production site
we run this application in docker, so it's better to keep your development process similar to the
production one.

### Full in-docker local development

#### Required software

To run container for development you need to have _Docker (Community Edition)_ installed, as well as
a `docker-compose-plugin` installed on your system.

For Debian-based systems use APT:

```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

For RPM-based systems:

```bash
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

#### How can I run it?

To keep things simple we've written `dev.py` script inside `tools` directory. It can run everything
for you, simply type `python3 dev.py run` or `./dev.py run`. No root permissions are needed.
All commands used with the script are listed under `./dev.py --help` and help for command `CMD`
under `./dev.py CMD --help` (e.g. `./dev.py run --help`).

There are 3 flags that you might want to use with `dev.py run`:

- `--create-admin` - create super user / admin account with the password of your choice
- `--create-data` - generate some semi-random data - the implementation can be found
  here: `src/conferences/management/commands/create_data.py`. This command also generates
  several user accounts `zosia[1-5]?@example.com` that can be accessed with password: `pass`.
- `--no-cache` - build the fresh copy of the container image (ignore docker cache)

#### I have run it - what is happening?

First, script needs to build the docker image. This process uses local cache, so it takes time
at the first run only, because docker has to pull `python` image and build every layer.
Then two containers have started: `zosia_db_1` with Postgres database and `zosia_web_1` with our
web application.

We mount some local folders so as to let you develop application without rebuilding docker every
time:

- `./app/src` as `/code/src`
- `./app/js` as `/code/js`
- `./app/static` as `/code/static`

Thanks to this, all changes you make in the code will be visible immediately inside the container.
**Remember that this works in both directions!** Every change you'll make in the container
will affect your local files (from the listed folders), because these are the same files, of
course :P

We tried to avoid side effects in our `dev.py` script, but sometimes it can't be achieved easily.
Some commands may create files inside listed folders. This files will be owned by `root`,
because they were created inside docker. You don't have to worry about them, we listed them in
`.gitignore` file, so they should not appear in `git status`.

Files created in directory `/code/static` are output from the webpack build system (these are JS
and CSS files). They will be created in your local filesystem and fortunately will be ignored by
version control. Moreover, NodeJS module required by our application are installed. They will
exist inside docker container only, so they won't be copied into your local filesystem. If you'd
like your JS file to be rebuilt after editing them, run command `./dev.py javascript watch`
in new terminal.

Next, we run migrations on database and, finally, start the web server. In terminal you will
see output/logs from django (e.g. queries to the database).

You can shut this server down anytime by clicking `CTRL+C`, but containers will be still alive.
If you want to start the web server again, just run `./dev.py server`.
If you want to shut all containers down, you need to run `./dev.py quit` command.

### Troubleshooting

```text
Creating network "zosia_default" with the default driver
ERROR: could not find an available, non-overlapping IPv4 address pool among the defaults to assign to the network
```

This error can appear during `docker compose up` command if you have VPN activated on your system.
There has been no solution found yet. You have to disconnect from VPN, run `docker compose up` and
when containers are finally up you may enable your VPN again.

---

```text
Creating network "zosia_default" with the default driver
ERROR: Failed to program FILTER chain: iptables failed: iptables --wait -I FORWARD -o br-123123123123 -j DOCKER: iptables v1.X.Y: Couldn't load target `DOCKER':No such file or directory
```

In case of that error just restart docker daemon service with this command:
`systemctl restart docker`

---

In case of any other problems it is recommended to rebuild the container with `--no-cache` option
(i.e. `./dev.py run --no-cache` or `./dev.py start --no-cache`).

## Hosting

### 2019-2020
We hosted ZOSIA registration site on AWS. We used an ECS cluster based on EC2 instances
to run the containers and ECR as a docker registry. All secrets (like database credentials,
different APIs keys, etc) were stored in the Parameter Store and loaded to the environment variables
on container startup. Deployments were conducted by CircleCI after every commit to the master
branch.
All deployment scripts used for that are placed in the `.ecs` directory.

### 2022 - 2023
We hosted the ZOSIA site on GCP App Engine with GCP SQL as Postgres managed database. Deployments
were still done using CircleCI pipelines.
