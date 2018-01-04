# Crawling test

## How to start?

* Run `docker-compose build`
* Run `docker-compose up -d mongo`
* Run `docker-compose run python`

## How to check?

* Run `docker-compose up -d mongo`
* Run `docker-compose run mongo bash`
  * Run `mongo mongo/testing`
  * Run `db.urls.find()`

## How to run tests?

* Run `python tests.py`
