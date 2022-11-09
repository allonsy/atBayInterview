# At Bay Home Assignment

## Setup
You will need the following software
* Python (version 3.4 or later)
* Docker
* Unix system (mac or linux)
  * Sorry, although the python is cross platform, integration with windows and docker is not included in the runner scripts

Run `./setup` from this directory to install dependencies (contained in [requirements.txt](requirements.txt))

## Execution
Run `./run` from this directory to run the program. It will start a fresh mongo instance within docker and then startup the ingest, process, and status programs accordingly

* By default `mongo` is hosted on port `27017`. To change this, change the `MONGO_PORT` variable in the `./run` script
* By default `ingest` is hosted on port `10550`. To change this, change the `INGEST_PORT` variable in the `./run` script
* By default `status` is hosted on port `10551`. To change this, change the `STATUS_PORT` variable in the `./run` script

In order to queue a cyber scan, visit (or `curl`) `localhost:10550` (use a standard `GET` request to the `/` path). This will queue a request and return the scan ID

In order to view all the available requests, visit (or `curl`) `localhost:10551` (use a standard `GET` request to the `/` path).
To view the status of a specific request, visit `localhost:10551/<SCAN_ID>`, replacing `<SCAN_ID>` with the desired scan id.
Trying to retrieve the status of a non-existent status ID will return a `Not Found` status and a `404`. 