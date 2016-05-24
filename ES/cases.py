#!/usr/bin/python
import argparse
import sys
import time
import subprocess

# Set a parser object
parser = argparse.ArgumentParser()
### Mandatory Parameters
parser.add_argument("--clients_min",
                    type=int, default=1,
                    help="The minum of CLIENTS")

parser.add_argument("--clients_max",
                    type=int, default=2,
                    help="The maxmun of CLIENTS")

parser.add_argument("--running_seconds",
                    type=int, default=60,
                    help="The running_seconds of per benchmark")

# Parse the arguments
args = parser.parse_args()
CLIENTS_MIN = args.clients_min
CLIENTS_MAX = args.clients_max
RUNNING_SECONDS = args.running_seconds
cmd = None

# Set variables from argparse output (for readability)
number_of_clients = None
running_seconds = None
optional_parameters = {
    "es_hosts": None,    # "10.10  10.11  10.12"
    "indices": None,
    "number_of_shards": None,
    "number_of_replicas": None,
    "refresh_interval": None,
    "number_of_metrics_per_bulk": None,
    "cleanup": None,
    "stats_interval": None
}


def append_optional_parameters(**kwargs):
    global cmd
    for key, val in kwargs.iteritems():
        if val is not None:
            cmd += "--"+key+" "+str(val)


def main():
    global cmd
    for number_of_clients in range(CLIENTS_MIN, CLIENTS_MAX+1):  # 1 client to 100 clients
        cmd = "./es_metrics_benchmark.py " + str(number_of_clients) + " " + str(RUNNING_SECONDS)+" "
        append_optional_parameters(**optional_parameters)
        subprocess.call(cmd, shell=True)
        time.sleep(RUNNING_SECONDS+15)

    sys.exit(-1)

if __name__ == "__main__":
  main()