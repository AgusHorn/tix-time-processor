# tix-time-processing
[![Build Status](https://travis-ci.org/TiX-measurements/tix-time-processor.svg?branch=master)](https://travis-ci.org/TiX-measurements/tix-time-processor)
[![codecov](https://codecov.io/gh/TiX-measurements/tix-time-processor/branch/master/graph/badge.svg)](https://codecov.io/gh/TiX-measurements/tix-time-processor)

This is the `tix-time-processor` microservice. It's main task is to recurrently process the data packets of every 
installation for each user, and post the data collected to the `tix-api`. It alsa uses the IP to AS service, to localize
the source of the packets.

It uses a Celery app to schedule the processing every 10 minutes. That is why it should be connected to the RabbitMQ 
service in the server.

## Installation 
**Currently in dev. Installation instructions are a wishful thinkng right now**  

The `tix-time-processor` is intended to be used a Docker container. So to use it, you just need to download the latest image 
and run it with docker.

It is necessary to create two volumes. One which will contain the reports from the `tix-time-condenser`. That is how this two 
micro-services communicate with each other.   
The other volume is the one which will contain the scheduler file.
  
## Configurations

The `tix-time-processor` uses a handful of environment variables to run. Most of them have defaults which are the bare 
minimum to be executed. But some of the most important not.

  * `TIX_REPORTS_BASE_PATH`: The path, either in the container or in the machine where the reports are found. (**Default**: '/tmp/reports')
  * `TIX_RABBITMQ_USER`: RabbitMQ user ()needed by Celery) (**Default**: 'guest')
  * `TIX_RABBITMQ_PASS`: RabbitMQ password (needed by Celery) (**Default**: 'guest')
  * `TIX_RABBITMQ_HOST`: RabbitMQ host (needed by Celery) (**Default**: 'localhost')
  * `TIX_RABBITMQ_PORT`: RabbitMQ port (needed by Celery) (**Default**: 5672)
  * `TIX_API_SSL`: If this environment variable has any value whatsoever (i.e.: `True`, `False`, `-1`, `sarasa`) then 
   HTTPS protocol communication with the API will be enabled. If left undefined or empty, it will use HTTP alone.  (**Default**: _Empty_)
  * `TIX_API_HOST`: The API host where is located (**Default**: 'localhost')
  * `TIX_API_PORT`: The API port in the host where is located(**Default**: 80 for HTTP, 443 for HTTPS)
  * `TIX_API_USER`: The API username for the `tix-time-processor` that is used to authenticate. If left empty, the POST 
  request wont be effectuated and the result will be left in the failed results' directory for the installation. (**Default**: _Epmty_)
  * `TIX_API_PASSWORD`: The API password for the `tix-time-processor` that is used to authenticate. If left empty, the 
  POST request wont be effectuated and the result will be left in the failed results' directory for the installation. (**Default**: _Empty_)
    
## How to run it

This a Celery scheduled app and has three modes of running.

  * As a standalone app
  * As a scheduler
  * As a worker
  
When the service is run in standalone mode, it will schedule and execute the tasks on its own. But since this is not the 
method preferred for production environment given the many complications it would have as a distributed service, the beat
and worker mode exist. The scheduler mode will serialize the tasks and queue them in the RabbitMQ Service. While the 
workers will take each of the serialized tasks and execute them. It is important to note that while many workers instances
may exists at the same time, only one scheduler instance must exists, because having more than one may derive in concurrency
problems. This is the same reason why in productive environments it is advised not to use the standalone mode.

To run it as a Celery app, outside the Docker container the following commands are available:

As a stand-alone app
```
$> celery -A processor.tasks worker -B [-s celerybeat_scheduler_file_path] [-l celery_log_level]
```

As a scheduler app
```
$> celery -A processor.tasks beat [-s celerybeat_scheduler_file_path] [-l celery_log_level]
```

As a worker app
```
$> celery -A processor.tasks worker [-l celery_log_level] 
```

If you want to use it as a Docker Container, you should create a volume or use the volume that the `tix-time-condenser` 
is using to drop the report files, and the volume that is used to store the scheduler file

```
$> docker volume create --name ReportsVolume
$> docker volume create --name SchedulerVolume
```

After that, you should simply need to run

```
$> docker run -e PROCESSOR_TYPE=<PROCESSOR_TYPE> -v ReportsVolume:/tmp/reports -v SchedulerVolume:/tmp/celerybeat-schedule.d -dit tixmeasurements/tix-time-processor:latest-<type>
```

Where the environment variable `PROCESSOR_TYPE` might take the following values:

  * `STANDALONE` (**This is the default value**)
  * `BEAT`
  * `WORKER`

This works for both, the standalone and the scheduler / beat type.

For the worker type, you should omit the SchedulerVolume, like this

```
$> docker run -e PROCESSOR_TYPE=WORKER -v ReportsVolume:/tmp/reports -dit tixmeasurements/tix-time-processor:latest-<type>
```

There are other configuration variables available for the Docker Container besides `PROCESSOR_TYPE`

  * `CELERY_BEAT_SCHEDULE_DIR`: The directory where the Celery Beat schedule file will be stored. (**Default**: /tmp/celerybeat-schedule.d)
  * `CELERY_LOG_LEVEL`: The logging level for the Celery app. (**Default**: INFO)

# Tests analysis
This module also contains a Jupyter Notebook for analyzing calibration tests results. This module can be used after running the calibration test described in the [tix-time-system-test](https://github.com/eduardoneira/tix-time-system-test) module, in order to analyze the results of those tests.

These instructions were tested on Ubuntu 16.04 (64 bits).

## Requirements
Check that you have python3 along with pip3 and virtualenv:

```sh
python3 --version
pip3 --version
virtualenv --version
```
If these packages are not installed, install them running the following:
```sh
sudo apt update
sudo apt install python3-dev python3-pip
sudo pip3 install -U virtualenv  # system-wide install
```

## Setup
From the `tix-time-processor` directory, execute:
```sh
virtualenv --no-site-packages -p python3 tix-processor-venv
source tix-processor-venv/bin/activate
```
The virtualenv name could be any name. Here we chose ```tix-processor-venv```.
Install dependencies in the virtualenv:
```sh
pip install -r requirements-notebook.txt
```
## Running the analysis
Before running this analysis, make sure you have the following files as a result of running the  test:
```
├── description.yml
├── network_usage.log
├── tix-time-client-logs
│   ├── 1543816931101-21731100485417-tix-log.json
│   ├── 1543816992082-21792081601989-tix-log.json
│   ├── 1543817053093-21853092557779-tix-log.json
│   ├── 1543817114112-21914111663645-tix-log.json
│   ├── 1543817175075-21975074536638-tix-log.json
│   ├── 1543817236110-22036109811562-tix-log.json
|   ...
│   ├── 1543838833090-43633089121888-tix-log.json
│   └── 1543838894094-43694093401424-tix-log.json
└── torrent_client.log
```
* `description.yml` : Test configuration file used during test
* `network_usage.log` : Log with the estimated download speed in kbps from the local interface
* `torrent_client.log` : Log with stdout of torrent client spawned during calibration test
* `tix-time-client-logs/` : Directory for tix-time-client log files. The naming format of the log files should be `<unix_timestamp>-<java_timestapmp>-tix-log.json`


### Generate the reports batches
First we need to group the log files generated by the TiX client into multiple batches. This is to imitate the way the tix-time-processor takes the files and computes them by separating them into different directories.
In order to run the formatter, simply run from `tix-time-processor/reports_batch_formatter`:
```sh
python formatter.py \
    --source_directory=path/to/tix-time-client-logs \
    --output_directory=path/to/output \
```
This will generate a file called ```batch-test-report.tar.gz``` in the ```output_directory```.  Extract the tar in a directory of its own (we will need to reference that directory later).
```sh
cd <output_directory>
mkdir batch-test-report
tar -xzf batch-test-report.tar.gz -C batch-test-report/
```

After running de formatter, you need to extract only the batches files.
These are named like: ```1721187934.json``` and NOT like ```1721187994501-13594483321220-tix-log.json```

### Launching the Notebook
In order to run the notebook for visualizing the results, from the `tix-time-processor` directory run:
```sh
jupyter notebook
```
This should open up a Jupyter Notebook in your browser. From there, open the `new_general_analysis_notebook.ipynb` notebook.
In the first cell of the notebook, you can specify the paths to the reports batches directory (generated in the previous step), the YAML configuration file used for the test, and the network usage log file. If you run the TIX client in one host and the torrent client in another host, then you will need the network usage file for both hosts. For example:
```sh
BATCHES_DIR = '/path/to/batch-test-report'
TEST_CONFIG_FILE = '/path/to/description.yml'
NET_USAGE_FILE='/path/to/network_usage.log'
NET_USAGE_TIX_FILE='/path/to/network_usage_tix_file.log'
```
Afterwards, you can simply execute all the cells in the notebook, and should be able to visualize the results.