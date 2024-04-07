# Django ping

## What is this?

This is an experimental project that implements running ping 
on a remote webserver (Django) on demand and sends its output 
to the browser.

Generally speaking, this project is not only about ping. 
It is about running tasks on demand on a remote webserver. 
It can be used to implement streaming from an IP camera 
on demand (while there are listeners) and in many other 
ways. Ping was used as an example. It's good because 
usually ping does not stop immediately and prints some 
summary after SIGTERM is sent.

Additionally, the following logic is implemented in this 
project:

1. If ping for the same IP is already running, the user 
   will be connected to view the output of the currently 
   running process.
2. If there are no listeners to a process, it will be 
   terminated automatically (after a grace period).
3. Each ping process has its own lifetime and will be 
   terminated after its lifetime is exceeded, even if 
   there are listening users.

Warning: This is not a library or a framework; 
it is a semi-finished product. You must manually adapt it
to your needs if you find it useful. Use it for inspiration
and take care.

## Stack

1. Django (5.0.3)
2. Django REST Framework (for API)
3. Channels (server sends data to client throughout websockets)
4. Celery (to run a process asynchronously and process its data)
5. Redis (as temporary data storage, also for Channels)

This project only supports Linux. It will not function correctly 
on Windows due to differences in how processes are implemented, 
particularly with Celery. However, you can explore using Docker 
or other alternatives to implement task queues and long-running 
tasks on Windows. Please note that this project has not been tested 
on macOS. 

## How to run

There are two options provided.

### Run via Docker

#### 1. Clone project

Clone the project from GitHub using any convenient method.

#### 2. Build and run Docker image

```
docker-compose up --build
```

#### 3. Apply migrations and create a test user

Visit container through cli.

```
sudo docker exec -it django_ping_webserver bash
```

Activate venv.

```
source venv/bin/activate
```

Apply migrations.

```
python manage.py migrate
```

Run 

```
python manage.py createsuperuser
```

and follow guide to create user. Then exit the container.

```
exit
```

#### 4. That's all!

You are ready to login. Go to http://127.0.0.1:8000 via your 
browser and provide user credentials you entered above.

### Run locally

This section assumes you are running Linux and have Python 3.10 or 3.11 or 3.12, and Redis server version 5.0 or above is available.
See more:

https://docs.djangoproject.com/en/5.0/releases/5.0/

https://github.com/redis/redis-py?tab=readme-ov-file#supported-redis-versions

#### 1. Clone project

Clone the project from GitHub using any convenient method.

#### 2. Create venv, activate and then install dependencies

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Provide configuration

Find `default.conf` in `django_ping` folder. Copy and rename it to `.conf`.
Provide Redis connection properties if you have different from defaults.

#### 4. Apply migrations and create a test user

Apply migrations.

```
python manage.py migrate
```

Run 

```
python manage.py createsuperuser
```

and follow guide to create user.

#### 5. Start Django and Celery

Start Django

```
python manage.py runserver
```

Start Celery

```
celery -A django_ping worker -l INFO -P gevent
```

#### 5. That's all!

You are ready to login. Go to http://127.0.0.1:8000 via 
your browser and provide user credentials you entered above.

## Conclusion

Thank you for your time on visiting this project.

If you found some bug or something else feel free to open an issue.
