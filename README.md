https://github.com/hfwittmann/financial-timeseries-dashboard

Pretty similar in design to https://github.com/hfwittmann/financial-timeseries-dashboard

Showing various Covid19 related Timeseries Plots and Maps.


This repo is used and described in the following blog post: https://arthought.com/new-version-of-covid19-dashboard .


To run, simply do the following:

In the the backend folder create a file with name .env with the following contents:
PYTHONPATH=.
HOST=localhost
In the the front end folder create a file with name .env with the following contents:
PYTHONPATH=.
HOST=backend
Now run

docker-compose -p deployment -f docker-compose.yml up --build -d
Your app should be now start to build. Depending on your system it might take a while.

After a while it should be up and running.

The dashboard should available at http://localhost:8501 The swagger ui should be available at local: http://localhost:5000/api/ui/#

In the backend folder you will find a sub-folder called data, with cached Data from the d6tflow package.
