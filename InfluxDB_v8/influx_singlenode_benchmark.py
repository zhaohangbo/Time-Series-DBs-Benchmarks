#!/usr/bin/python

import argparse

from influxdb.influxdb08 import InfluxDBClient
from influxdb.influxdb08.client import InfluxDBClientError

import influx_metrics_generator

import influx_benchmark_helper
from influx_benchmark_helper import increment_success, increment_failure, increment_size
from influx_benchmark_helper import has_timeout, print_stats_worker, print_stats

from threading import Lock, Thread, Condition

import sys
import time
import traceback



def parse_args():
    parser = argparse.ArgumentParser(description='Benchmark InfluxDB')

    parser.add_argument('--host', type=str, required=False, default='localhost',
                        help='Hostname influxdb http API, default localhost')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='Port influxdb http API, default 8086')
    parser.add_argument('--batch_size', type=int, required=False, default=1000,
                        help='Number of metrics per batch, limited, default 1000 ,can not bigger than 100000000')
    parser.add_argument("--min_num_of_clients", type=int, required=False, default=1,
                        help="The minimum number of client threads")
    parser.add_argument("--max_num_of_clients", type=int, required=False, default=2,
                        help="The maximum number of client threads")
    parser.add_argument("--running_seconds", type=int, required=False, default=60,
                        help="The number of seconds to run")
    parser.add_argument("--stats_interval", type=int,  required=False, default=30,
                        help="Number of seconds to wait between stats prints (default 30)")
    return parser.parse_args()


# USER & PASSWORD & DBNAME
USER = 'root'
PASSWORD = 'root'
DBNAME = 'benchmark_db'

# Global Varible
influx_client = None
series_for_multi_clients = {}
sizes_for_multi_clients = {}
#retention_policy_name = 'benchmark_retention_policy'
series_name = "benchmark_series"

# Constant
HOST = 'localhost'
PORT = 8086
MIN_NUM_OF_CLIENTS = 1
MAX_NUM_OF_CLIENTS = 2
BATCH_SIZE = 1000
RUNNING_SECONDS = 60
STATS_INTERVAL = 30

def init():
    global HOST
    global PORT
    global MIN_NUM_OF_CLIENTS
    global MAX_NUM_OF_CLIENTS
    global BATCH_SIZE
    global RUNNING_SECONDS
    global STATS_INTERVAL

    args = parse_args()

    HOST = args.host
    PORT = args.port
    MIN_NUM_OF_CLIENTS = args.min_num_of_clients
    MAX_NUM_OF_CLIENTS = args.max_num_of_clients
    BATCH_SIZE = args.batch_size
    RUNNING_SECONDS = args.running_seconds
    STATS_INTERVAL = args.stats_interval


def batch_write_worker(client_id):
    # Running until timeout
    while not has_timeout():
        try:
            #print("A batch begins...... \n")
            batch_start_time = time.time()

            # Perform the batch operation !!!!!!!!!!!!!!!!!!
            #influx_client.write_points(series_for_multi_clients[client_key], batch_size=BATCH_SIZE, retention_policy=retention_policy_name)
            influx_client.write_points(series_for_multi_clients[client_id], batch_size=BATCH_SIZE)
            print("Client_"+client_id),
            print("Batch execution time:  %s  seconds \n" % (time.time() - batch_start_time))
            #print("A batch ends...... \n")

            # Adding to success batch
            increment_success()
            # Adding to size (in bytes)
            increment_size(sizes_for_multi_clients[client_id])

        except Exception as e:
            # Failed. incrementing failure
            increment_failure()
            print(e.message)
            traceback.print_exc()

def generate_clients(num_of_clients):
    # Clients placeholder
    global series_for_multi_clients
    global sizes_for_multi_clients
    list_clients = []

    # Iterate over the clients count
    for i in range(num_of_clients):

        # Generate Batch of Metrics for a specific client
        client_id = str(i)
        series, series_total_physical_size = influx_metrics_generator.generate_batch(batch_size=BATCH_SIZE, series_name=series_name, client_tag=client_id)
        series_for_multi_clients[client_id] = series
        sizes_for_multi_clients[client_id] = series_total_physical_size

        # Be aware, without comma here, would throw exception "takes exactly 1 argument (8 given)"
        # Without comma, causes Python to iterate over the string and treat each character as an argument.
        a_client_thread = Thread(target=batch_write_worker, args=(client_id,))
        a_client_thread.daemon = True

        # Create a thread and push it to the list
        list_clients.append(a_client_thread)

    # Return the clients
    return list_clients


def test_case_of_n_clients(num_of_clients):
    global influx_client
    # Get Client
    influx_client = InfluxDBClient(HOST, PORT, USER, PASSWORD, DBNAME)

    # Greate Database
    print("Create database: " + DBNAME)
    try:
        influx_client.create_database(DBNAME)
    except InfluxDBClientError:
        # Drop and create
        influx_client.delete_database(DBNAME)
        #influx_client.drop_database(DBNAME)
        influx_client.create_database(DBNAME)

    # Add retention policy
    print("Create a retention policy")
    #influx_client.create_retention_policy(retention_policy_name, '3d', 3, default=True)

    # Init benchmark_helper
    STARTED_TIMESTAMP = int(time.time())
    influx_benchmark_helper.init(STARTED_TIMESTAMP, RUNNING_SECONDS, STATS_INTERVAL, BATCH_SIZE)


    print("Generating  clients.. "),
    clients = generate_clients(num_of_clients)
    print("Done!\n")

    print("Run multiple clients and do batch writes "),
    # Run the clients! Do batch writes with multi clients
    map(lambda thread: thread.start(), clients)
    print("Done!\n")

    # Create and start the print stats thread
    stats_thread = Thread(target=print_stats_worker(num_of_clients))
    stats_thread.daemon = True
    stats_thread.start()

    # And join them all but the stats, that we don't care about
    map(lambda thread: thread.join(), clients)
    # A call to thread1.join() blocks the thread in which you're making the call, until thread1 is finished.
    # It's like wait_until_finished(thread1).

    # Record final results into report.txt file
    is_final_result = True
    print_stats(num_of_clients, is_final_result)

    time.sleep(2)

    # Do query
    # query = "SELECT MEAN(value) FROM %s WHERE time > now() - 20d GROUP BY time(500m)" % (series_name)
    # result = influx_client.query(query)
    # print("Result: {0}".format(result))

    # Drop Database
    print("Drop database: " + DBNAME)
    influx_client.delete_database(DBNAME)


def check_paras():
    global MIN_NUM_OF_CLIENTS
    global MAX_NUM_OF_CLIENTS
    global RUNNING_SECONDS
    global BATCH_SIZE
    if MIN_NUM_OF_CLIENTS < 0:
        MIN_NUM_OF_CLIENTS = 1
    if MAX_NUM_OF_CLIENTS < 0 or MAX_NUM_OF_CLIENTS < 1:
        MAX_NUM_OF_CLIENTS = MIN_NUM_OF_CLIENTS + 1
    if RUNNING_SECONDS < 0:
        RUNNING_SECONDS = 60
    if BATCH_SIZE > 100000000:  # 7 zeros
        BATCH_SIZE = 100000

def main():
    check_paras()
    for number_of_clients in range(MIN_NUM_OF_CLIENTS, MAX_NUM_OF_CLIENTS+1):  # 1 client to 100 clients
        test_case_of_n_clients(number_of_clients)
        time.sleep(RUNNING_SECONDS+15)
    sys.exit(-1)

if __name__ == '__main__':
    init()
    main()
