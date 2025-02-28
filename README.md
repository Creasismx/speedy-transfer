# Speedy Transfers

## Environment

To start the application it is necessary to include the .env file

## Build

```shell
docker-compose build
```

```shell
cd templates/assets
npm install
npm run watch
```

## Running the application

The application is built with Django and already has all environment configured with docker. To start the application you will need `docker` and `docker-compose` installed on the machine. Having that you may run:

```shell
docker-compose up
```

And then the application and database will be started:

```shell
Starting speedy_db ... done
Starting speedy_app        ... done
```

The application will be avaible on _PORT 8000_ by default, but it's configurable via `docker-compose.yml` file as an environment variable.


## Running makemigrations

```shell
docker exec -ti app python /code/manage.py makemigrations
```

## Running empty makemigrations

```shell
docker exec -ti app python /code/manage.py makemigrations app_name --empty
```

## Running the migrations

```shell
docker exec -ti app python /code/manage.py migrate
```

## Use django shell

```shell
docker exec -ti app python /code/manage.py shell
```

## Create super user

```shell
docker exec -ti app python /code/manage.py createsuperuser
```

## Create translations

```shell
django-admin makemessages -l en

```

## Create compile messages

```shell
django-admin compilemessages --ignore apps

```