#!/usr/bin/python

# Using argparse to parse cli arguments
import argparse

# Import threading essentials
from itertools import cycle, islice
from threading import Lock, Thread, Condition

# For randomizing
import string

import random
from random import randint, choice

# To get the time
import time

# https://elasticsearch-py.readthedocs.io/en/master/
from datetime import datetime

# For misc
import sys

# For json operations
import json
import traceback


# Try and import elasticsearch
try:
    from elasticsearch import Elasticsearch,  helpers, serializer
    from elasticsearch.client import IndicesClient

except:
    print("Could not import elasticsearch..")
    print("Try: pip install elasticsearch")
    sys.exit(1)

# Set a parser object
parser = argparse.ArgumentParser()


### Mandatory Parameters
parser.add_argument("number_of_clients",
                    type=int,
                    help="The number of threads to write from")

parser.add_argument("running_seconds",
                    type=int,
                    help="The number of seconds to run")


### Optional Parameters
parser.add_argument("--es-hosts",
                    nargs='+', default=["10.10.10.10", "10.10.10.11"],
                    help="The address of your cluster (no protocol or port), (default ['10.10.10.10','10.10.10.11'])")

parser.add_argument("--indices",
                    type=int, default=8,
                    help="The number of indices to write to (default 8)")

parser.add_argument("--number-of-shards",
                    type=int, default=5,
                    help="Number of shards per index (default 5)")

parser.add_argument("--number-of-replicas",
                    type=int, default=1,
                    help="Number of replicas per index (default 1)")

parser.add_argument("--refresh_interval",
                    type=int, default=1,
                    help="Index refresh interval (default 1)")

parser.add_argument("--number-of-metrics-per-bulk",
                    type=int, default=50000,
                    help="Number of metric docs per bulk request (default 50000)")

parser.add_argument("--no-cleanup",
                    dest='cleanup', action='store_false',
                    help="Don't delete the indices upon finish (Default:cleanup=True, --no-cleanup turns it to False)")

parser.set_defaults(cleanup=True)

parser.add_argument("--stats-interval",
                    type=int, default=30,
                    help="Number of seconds to wait between stats prints (default 30)")

# Parse the arguments
args = parser.parse_args()

# Set variables from argparse output (for readability)
NUMBER_OF_INDICES =          args.indices
NUMBER_OF_CLIENTS =          args.number_of_clients

ES_HOSTS    =                args.es_hosts
RUNNING_SECONDS   =          args.running_seconds
NUMBER_OF_SHARDS =           args.number_of_shards
NUMBER_OF_REPLICAS =         args.number_of_replicas
REFRESH_INTERVAL   =         args.refresh_interval
NUMBER_OF_METRICS_PER_BULK = args.number_of_metrics_per_bulk
CLEANUP =                    args.cleanup
INTERVAL_BETWEEN_STATS =     args.stats_interval

# timestamp placeholder
STARTED_TIMESTAMP = 0

# Constant


# Placeholders
success_bulks = 0
failed_bulks  = 0
total_size    = 0
indices = []
types = ["long_metrics",
         "integer_metrics",
         "short_metrics",
         "byte_metrics",
         "double_metrics",
         "float_metrics",
         "boolean_metrics"]

es = None # Will hold the elasticsearch session
es_indices = None
# Thread safe
success_lock = Lock()
fail_lock = Lock()
size_lock = Lock()


def generate_indices():
    # Placeholder
    list_indices = []

    # Iterate over the indices count
    for i in range(NUMBER_OF_INDICES):
        # Generate the index name
        index_name = "metrics_"+str(i)
        # Push it to the list
        list_indices.append(index_name)

        try:
            # And create it in ES with the shard count and replicas
            es.indices.create(index=index_name, body={"settings": {"number_of_shards": NUMBER_OF_SHARDS,
                                                                   "number_of_replicas": NUMBER_OF_REPLICAS,

                                                                    "index": {
                                                                                  "refresh_interval": str(REFRESH_INTERVAL)+"s"
                                                                             }
                                                                   }})

        except:
            print("Could not create index. Is your cluster ok?")
            sys.exit(1)

    # Return the indices
    return list_indices


def cleanup_indices():

    # Iterate over all indices and delete those
    for cur_index in indices:
        try:
            # Delete the index
            es.indices.delete(index=cur_index, ignore=[400, 404])

        except:
            print("Could not delete index: {0}. Continue anyway..".format(cur_index))





def main():
    # Define the globals
    global indices
    global STARTED_TIMESTAMP
    global es
    global es_indices
    try:
        # Initiate the elasticsearch session using ES low-level client.
        # By default nodes are randomized before passed into the pool and round-robin strategy is used for load balancing.
        es = Elasticsearch(ES_HOSTS, timeout=30)
        es_indices = IndicesClient(es)

    except:
        print("Could not connect to elasticsearch!")
        sys.exit(1)

    print("Creating indices.. \n"),
    indices = generate_indices()
    print("Done!\n")

    print("GET Settings \n"),
    print json.dumps(es_indices.get_settings(index="_all"), sort_keys=True,indent=4, separators=(',', ': '))
    print("Done!\n")

    # We will Clean up the indices by default
    # Default: True
    if CLEANUP:
        print("Cleaning up created indices.. "),
        cleanup_indices()
        print("Done!\n")

if __name__ == "__main__":
    # Main runner
    try:
        main()

    except Exception as e:
        print("Got unexpected exception. probably a bug, please report it.")
        print("")
        print(e.message)
        traceback.print_exc()

        sys.exit(1)