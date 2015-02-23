# Project IRIS

------

## Code Setup
For compatibility issues with the scripts deployed in Seerlabs, it is advisable to always setup the main folder as `/appl/iris` and the environment folder as `/appl/iris-env`


## Running the App
Scripts for running the main Flask App with uWSGI are now available under /appl/iris/. There are currently two modes:

#### Running uWSGI in CLI
- ./start.sh

#### Running uWSGI in Daemonized mode
- ./startd.sh to start
- ./stopd.sh to stop
- This will run the app on the background (Will run even when the terminal is closed)
- Logs for uWSGI can be found in /var/log/iris.uwsgi.log
