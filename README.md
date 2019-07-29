# zosia16-site
Django 2.2 version of ZOSIA registration page.

## Development

The preferred approach is to use a docker for development. And don't worry we tried to make it as easy as possible. Of course if you really not into containerisation you can try to run it without docker, but it will be harder to debug OS related bugs. Besides on production site we run this application in docker so it's better to keep your development as congenial to the production as possible.

### Local development (without docker)
[Moved here](local_development.md)

### Full in-docker local development 

#### Software you need:

To run docker container obviously you need Docker (community edition). Additionally you need to install `docker-compose`. 

On Debian based system you can do it like that:
```
sudo apt install docker-ce docker-compose 
```

`docker-compose` can be also installed with `pip`.


#### How should I run it?

To make it as easy as possible we create `dev.sh` script that will run everything for you.
You just have to run it like that: `./dev.sh one_click`. You don't need root permissions for that.

#### I run it - what is happening?

First script need to build the docker image. This process use local cache, so it's long only at the first time, because docker have to pull `python` image and build every layer. 

After that two containers are started `zosia_db_1` with postgess database and `zosia_web_1` with our app.

We mount some local folders to allow you develop application without rebuilding docker.
- `./app/src` as `/code/src`
- `./app/js` as `/code/js`
- `./app/static` as `/code/static`

Thanks to that all changes you make in code will be visible immediately inside container, **but remember** that it's working in both direction. Every change you will make in container will affect your local files (from the listed folders), because these are the same files :P

We tried to avoid side effect in our `dev.sh` script, but sometimes it can not be easily achieved. So some commands may create files inside listed folders. This files will be owned by `root`, because they were created inside docker. You don't have to worry about them, we put them on `gitignore` list, so they shouldn't appear in `git status`.

*TODO: describe js part* 

After that we run migration on database and finally we starting webserver. What you will see now in terminal is the output/logs from django - e.g. queries to the database. 

You can shutdown this server anytime by clicking `CTRL+C` but containers will be still alive. If you want to shut them down you need to run `./dev.sh shutdown` command. If you want to start webserver again just run `./dev.sh runserver`.

### Troubleshooting

```
Creating network "zosia_default" with the default driver
ERROR: could not find an available, non-overlapping IPv4 address pool among the defaults to assign to the network
```

That error can appears in during `docker-compose up` if you have VPN activated on your system. There is no solution for that. You have to disconnect from VPN, run `docker-compose up` and when containers are finally up you can enable your VPN again.

