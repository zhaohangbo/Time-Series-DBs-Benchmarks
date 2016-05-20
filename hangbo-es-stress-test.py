#!/usr/bin/python

# Using argparse to parse cli arguments
import argparse

# Import threading essentials
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
    from elasticsearch import Elasticsearch
    from elasticsearch import helpers
    from elasticsearch import serializer

except:
    print("Could not import elasticsearch..")
    print("Try: pip install elasticsearch")
    sys.exit(1)

# Set a parser object
parser = argparse.ArgumentParser()

#es_address 10.10.10.10 indices 3 documents 10 clients 3 seconds 60

# Adds all params
parser.add_argument("number_of_clients",
                    type=int,
                    help="The number of threads to write from")

parser.add_argument("running_seconds",
                    type=int,
                    help="The number of seconds to run")



parser.add_argument("--es-hosts",
                    nargs='+',default=["10.10.10.10","10.10.10.11"],
                    help="The address of your cluster (no protocol or port), (default ['10.10.10.10','10.10.10.11'])")

parser.add_argument("--indices",
                    type=int, default=8,
                    help="The number of indices to write to (default 8)")

parser.add_argument("--number-of-shards",
                    type=int, default=3,
                    help="Number of shards per index (default 3)")

parser.add_argument("--number-of-replicas",
                    type=int, default=1,
                    help="Number of replicas per index (default 1)")

parser.add_argument("--number-of-metrics-per-bulk",
                    type=int, default=1000,
                    help="Number of metric docs per bulk request (default 1000)")

parser.add_argument("--cleanup",
                    default=False, action='store_true',
                    help="Don't delete the indices upon finish")

parser.add_argument("--stats-interval",
                    type=int, default=30,
                    help="Number of seconds to wait between stats prints (default 30)")

# Parse the arguments
args = parser.parse_args()

# Set variables from argparse output (for readability)
ES_HOSTS    =                args.es_hosts
NUMBER_OF_INDICES =          args.indices
NUMBER_OF_CLIENTS =          args.number_of_clients
RUNNING_SECONDS   =          args.running_seconds
NUMBER_OF_SHARDS =           args.number_of_shards
NUMBER_OF_REPLICAS =         args.number_of_replicas
NUMBER_OF_METRICS_PER_BULK = args.number_of_metrics_per_bulk
MAX_FIELDS_PER_DOCUMENT =    args.max_fields_per_document
MAX_SIZE_PER_FIELD =         args.max_size_per_field
CLEANUP =                 args.cleanup
INTERVAL_BETWEEN_STATS =     args.stats_interval

# timestamp placeholder
STARTED_TIMESTAMP = 0

# Constant
SYS_MAXINT=sys.maxint

# Placeholders
success_bulks = 0
failed_bulks  = 0
total_size    = 0
indices   = []
types     = ["int_metrics","float_metrics","boolean_metrics"]
documents = []
documents_templates = []
es = None  # Will hold the elasticsearch session

# Thread safe
success_lock = Lock()
fail_lock = Lock()
size_lock = Lock()


# Helper functions
def increment_success():
    # First, lock
    success_lock.acquire()
    try:
        # Using globals here
        global success_bulks
        # Increment counter
        success_bulks += 1
    finally:  # Just in case
        # Release the lock
        success_lock.release()


def increment_failure():
    # First, lock
    fail_lock.acquire()
    try:
        # Using globals here
        global failed_bulks
        # Increment counter
        failed_bulks += 1
    finally:  # Just in case
        # Release the lock
        fail_lock.release()


def increment_size(size):
    # First, lock
    size_lock.acquire()
    try:
        # Using globals here
        global total_size
        # Increment counter
        total_size += size
    finally:  # Just in case
        # Release the lock
        size_lock.release()


def has_timeout():
    # Match to the timestamp
    if (STARTED_TIMESTAMP + RUNNING_SECONDS) > int(time.time()):
        return False
    return True


# Just to control the minimum value globally (though its not configurable)
def generate_random_int(max_size):

    try:
        return randint(1, max_size)
    except:
        print("Not supporting {0} as valid sizes!".format(max_size))
        sys.exit(1)


# Generate a random string with length of 1 to provided param
def generate_random_string(max_size):
    #''.join(choice(string.ascii_lowercase)) will randomly generate a letter
    #random.choice('abcdefghij')  # Choose a random element
    return ''.   join(choice(string.ascii_lowercase) for _ in range(generate_random_int(max_size)))


def generate_int_metric():
    int_metric = {}
    int_metric["@timestamp"] =datetime.now().isoformat()
    random_int = generate_random_int(SYS_MAXINT)
    int_metric["value"]      =random_int

    # Return the metric with a random value
    return int_metric

def generate_float_metric():
    float_metric = {}
    float_metric["@timestamp"] =datetime.now().isoformat()
    random_float = random.uniform(0, 1000000);
    float_metric["value"]      =random_float

    # Return the metric with a random value
    return float_metric

def generate_boolean_metric():
    bool_metric = {}
    bool_metric["@timestamp"] =datetime.now().isoformat()
    random_bool = bool(random.getrandbits(1))
    bool_metric["value"]      =random_bool
    return bool_metric

def get_metric_by_type_name(type_name):
    if(type_name=="int_metrics"):
        return generate_int_metric()
    if(type_name=="float_metrics"):
        return generate_float_metric()
    if(type_name=="boolean_metrics"):
        return generate_boolean_metric()

# Create a document template
# Generate doc with random numder of fields
def generate_document():
    temp_doc = {}
    # Iterate over the max fields
    # the loop variable '_' isn't actually used.
    for _ in range(generate_random_int(MAX_FIELDS_PER_DOCUMENT)):
        # Generate a field, with random content
        temp_doc[generate_random_string(10)] = generate_random_string(MAX_SIZE_PER_FIELD)
    # Return the created document
    return temp_doc  # return {"tkyfb": "ggids", "bigun": "lmqtl", "ikvku": "whlgv", "qqbno": "tpake", "xptxx": "pgcjw"}


def a_bulk():
    es = Elasticsearch()
    actions = []

    for j in range(0, 10):
        action = {
            "_index": "tickets-index",
            "_type": "tickets",
            "_id": j,
            "_source": {
                "any":"data" + str(j),
                "timestamp": datetime.now()
                }
            }

        actions.append(action)

    if len(actions) > 0:
        helpers.bulk(es, actions)

def bulk_metrics_worker():
    # Running until timeout
    while not has_timeout():

        cur_bulk  =""

        # Iterate over the bulk size
        for _ in range(NUMBER_OF_METRICS_PER_BULK):
            #Randomly pick a type
            type_name = choice(types)
            # Generate the bulk operation, here {0} means the 0-th argument
            cur_bulk += "{0}\n".format(json.dumps({"index": {"_index": choice(indices), "_type": type_name}}))
            cur_bulk += "{0}\n".format(json.dumps(get_metric_by_type_name(type_name)))
            #cur_bulk += "{0}\n".format(json.dumps(get_metric_by_type_name(type_name),default=serializer.JSONSerializer))

        try:
            # Perform the bulk operation !!!!!!!!!!!!!!!!!!
            es.bulk(body=cur_bulk)
            # Adding to success bulks
            increment_success()
            # Adding to size (in bytes)
            increment_size(sys.getsizeof(str(cur_bulk)))

        except:
            # Failed. incrementing failure
            increment_failure()

def generate_clients():
    # Clients placeholder
    list_clients = []
    # Iterate over the clients count
    for _ in range(NUMBER_OF_CLIENTS):
        a_client_thread = Thread(target= bulk_metrics_worker)
        a_client_thread.daemon = True
        # Create a thread and push it to the list
        list_clients.append(a_client_thread)

    # Return the clients
    return list_clients


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
                                                                   "number_of_replicas": NUMBER_OF_REPLICAS}})

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


def print_stats():

    # Calculate elpased time
    elapsed_time = (int(time.time()) - STARTED_TIMESTAMP)

    # Calculate size in MB
    size_mb = total_size / 1024 / 1024

    # Protect division by zero
    if elapsed_time == 0:
        mbs = 0
    else:
        mbs = size_mb / float(elapsed_time)

    # Print stats to the user
    print("Elapsed time: {0} seconds".format(elapsed_time))
    print("Successful bulks: {0} ({1} documents)".format(success_bulks, (success_bulks * NUMBER_OF_METRICS_PER_BULK)))
    print("Failed bulks: {0} ({1} documents)".format(failed_bulks, (failed_bulks * NUMBER_OF_METRICS_PER_BULK)))
    print("Indexed approximately {0} MB which is {1:.2f} MB/s".format(size_mb, mbs))
    print("")


def print_stats_worker():

    # Create a conditional lock to be used instead of sleep (prevent dead locks)
    lock = Condition()

    # Acquire it
    lock.acquire()

    # Print the stats every STATS_FREQUENCY seconds
    while not has_timeout():
        # Wait for timeout
        lock.wait(INTERVAL_BETWEEN_STATS)
        # To avoid double printing
        if not has_timeout():
            # Print stats
            print_stats()


def main():
    # Define the globals
    global documents_templates
    global indices
    global STARTED_TIMESTAMP
    global es
    try:
        # Initiate the elasticsearch session
        es = Elasticsearch(ES_HOSTS)

    except:
        print("Could not connect to elasticsearch!")
        sys.exit(1)

    print("Generating documents and workers.. "),
    # Generate the clients
    clients = generate_clients()
    # Generate docs
    #documents_templates = generate_documents()# doc_templates for randomly choose
    print("Done!\n")


    print("Creating indices.. \n"),
    indices = generate_indices()
    print("Done!\n")

    # Set the timestamp
    STARTED_TIMESTAMP = int(time.time())

    print("Starting the test. Will print stats every {0} seconds.".format(INTERVAL_BETWEEN_STATS))
    print("The test would run for {0} seconds, but it might take a bit more "
          "because we are waiting for current bulk operation to complete. \n".format(RUNNING_SECONDS))

    # Run the clients!
    map(lambda thread: thread.start(), clients)

    # Create and start the print stats thread
    stats_thread = Thread(target=print_stats_worker)
    stats_thread.daemon = True
    stats_thread.start()

    # And join them all but the stats, that we don't care about
    map(lambda thread: thread.join(), clients)
    # A call to thread1.join() blocks the thread in which you're making the call, until thread1 is finished.
    # It's like wait_until_finished(thread1).
    # So here ,it pauses the main process to wait the clients to finish.


    print("\nTest is done! Final results:")
    print_stats()

    # Don't Cleanup, unless we are told to
    # Default: False
    if CLEANUP:
        print("Cleaning up created indices.. "),
        cleanup_indices()
        print("Done!\n")


# Main runner
try:
    main()

except Exception as e:
    print("Got unexpected exception. probably a bug, please report it.")
    print("")
    print(e.message)
    traceback.print_exc()

    sys.exit(1)