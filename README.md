# At Bay Home Assignment

## Setup
You will need the following software
* Python (version 3.4 or later)
* Docker
* Unix system (mac or linux)
  * Sorry, although the python is cross platform, integration with windows and docker is not included in the runner scripts

Run `./setup` from this directory to install dependencies (contained in [requirements.txt](requirements.txt)) along with mongo.

## Execution
Run `./run` from this directory to run the program. It will start a fresh mongo instance within docker and then startup the ingest, process, and status programs accordingly

* By default `mongo` is hosted on port `27017`. To change this, change the `MONGO_PORT` variable in the `./run` script
* By default `ingest` is hosted on port `10550`. To change this, change the `INGEST_PORT` variable in the `./run` script
* By default `status` is hosted on port `10551`. To change this, change the `STATUS_PORT` variable in the `./run` script

In order to queue a cyber scan, visit (or `curl`) `localhost:10550` (use a standard `GET` request to the `/` path). This will queue a request and return the scan ID

In order to view all the available requests, visit (or `curl`) `localhost:10551` (use a standard `GET` request to the `/` path).
To view the status of a specific request, visit `localhost:10551/<SCAN_ID>`, replacing `<SCAN_ID>` with the desired scan id.
Trying to retrieve the status of a non-existent status ID will return a `Not Found` status and a `404`.

In order to quit the program, hit CTRL-C from the terminal. It will automatically kill all sub-programs

## Design Analysis

There are 3 components in the program. The Ingest component listens on HTTP for requests, when a request comes in, it generates a unique ID and then saves that ID to the mongo DB with status `Accepted`. Since there is very little logic here for each request, it results in a very lightweight server that can handle multiple requests at the same time and perform well under load.

The second component is Process. This component queries mongo for any requests in the accepted state and, one-by-one, processes them. In order to mock out this step, the program randomly waits somewhere between 1 and 5 seconds. Additionally, it mocks failure by randomly failing scans based on a certain failure ratio. 
In order to change the time that process waits, please change the `MIN_SLEEP` and `MAX_SLEEP` variables in [process/app.py](process/app.py). Additionally, to change the failure ratio, change the `CHANCE_OF_FAILURE` variable in [process/app.py](process/app.py). A value of `0.1` means a `10%` chance of failure.
If there are no requests in the `Accepted` state, the program will wait for 1 second and then retry. In a message queue system, this wait isn't necessary as the program simply waits for the next message. This can be accomplished with mongo via mongo change streams but was out of scope for this assignment.

The third component is Status. This is also a lightweight server that queries mongo for a given scan_id and looks up its status in the mongo database.
It then returns that value to the user (or 404 if the scan id doesn't exist).

### Scaling

The Ingest and Status servers are very easily scaled here. For example, we can spin up as many instances of Ingest and Status as we want (assuming they are all on different ports) and the program will still function perfectly fine.
If you wish to try this, navigate to the `ingest` directory, run `. ../pythonEnv/bin/active` to enter the python environment sandbox, run `export MONGO_PORT=27017` (or whichever port mongo is on), and then run `python -m flask run --port $INGEST_PORT`, changing `$INGEST_PORT` to a fresh port. You can spin up as many of these as you wish and the process system will continue to pick up requests from any instance.
The same can be done for the status component in the `status` directory.

The UUIDs are generated according to RFC4122 which ensures that they are unique without having to sync up the instances of the ingest service which allows this program to scale.
Since the UUIDs are unique, there isn't a chance of race conditions or need for synchronization between the servers.

In Production, without the time and setup constraints of this assignment, I would recommend 2 options:

1. We spin up a bunch of ingest and status servers as needed and put them behind an AWS application load balancer which is a scalable load balancer that can handle extremely large loads. This, together with a scaling mongo cluster, will easily scale to meet the demands of any large request load.

2. We can use a shared message bus like Kafka/RabbitMQ/Celery which are both large scale message queues. In this scenario, requests to ingest get put on the bus and the next available ingest server picks it up on the ingest topic, generates an ID, and places it on the bus for the Process component to process. This approach makes a lot of sense in many ways and wasn't implemented in this example because mocking out these systems would have essentially resulted in a mongoDB/HTTP communication setup anyway. In production/real life however, this approach can be quite valuable.

Both of these approaches have various pros and cons but both have the ability to scale to very large loads and process many requests in parallel.

### Why Mongo?

In this case, mongo is a good fit for the problem. IDs are generated according to RFC 4122 which nearly guarantees unique IDs (within the human lifetime).
Therefore, we don't need a database that has ACID guarantees like a SQL system. Instead, we want a database that scales well into a large cluster for maximum availability and read/write speeds.
Mongo fits this quite nicely as it scales very well into clusters and has high availability with high read/write speeds so long as the edits are not to the same document (given that the UUIDs are unique, this is a safe bet).