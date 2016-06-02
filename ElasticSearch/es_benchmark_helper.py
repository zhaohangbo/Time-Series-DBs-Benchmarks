import time
from threading import Lock, Thread, Condition


# Placeholders
success_bulks = 0
failed_bulks  = 0
total_size    = 0

# Thread safe
success_lock = Lock()
fail_lock = Lock()
size_lock = Lock()

# timestamp placeholder
STARTED_TIMESTAMP = 0
RUNNING_SECONDS = 0
INTERVAL_BETWEEN_STATS = 0
NUMBER_OF_METRICS_PER_BULK = 0

def init ( a_STARTED_TIMESTAMP, a_RUNNING_SECONDS, a_INTERVAL_BETWEEN_STATS, a_NUMBER_OF_METRICS_PER_BULK):
    global STARTED_TIMESTAMP
    global RUNNING_SECONDS
    global INTERVAL_BETWEEN_STATS
    global NUMBER_OF_METRICS_PER_BULK
    STARTED_TIMESTAMP = a_STARTED_TIMESTAMP
    RUNNING_SECONDS = a_RUNNING_SECONDS
    INTERVAL_BETWEEN_STATS = a_INTERVAL_BETWEEN_STATS
    NUMBER_OF_METRICS_PER_BULK = a_NUMBER_OF_METRICS_PER_BULK

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
    if (int(time.time()) < STARTED_TIMESTAMP + RUNNING_SECONDS):
        return False
    return True

def print_stats(NUMBER_OF_CLIENTS, isFinal):

    # Calculate elpased time
    elapsed_time = (int(time.time()) - STARTED_TIMESTAMP)
    # Calculate size in MB
    size_mb = total_size / 1024 / 1024

    # Protect division by zero
    if elapsed_time == 0:
        mbs_per_sec = 0
        doc_per_sec = 0
    else:
        mbs_per_sec = size_mb / float(elapsed_time)
        doc_per_sec = (success_bulks * NUMBER_OF_METRICS_PER_BULK) / float(elapsed_time)

    if success_bulks == 0:
        mbs_per_bulk = 0
    else:
        mbs_per_bulk = size_mb / float(success_bulks)

    # Print stats to the user
    if isFinal:
        print("------------------------------------")
        print("Test case of clients number={0} is done! Final results:".format(NUMBER_OF_CLIENTS))
        print("------------------------------------")
    print("Clients number: {0}".format(NUMBER_OF_CLIENTS))
    print("Elapsed time: {0} seconds".format(elapsed_time))
    print("Successful bulks: {0} ({1} documents)".format(success_bulks, (success_bulks * NUMBER_OF_METRICS_PER_BULK)))
    print("Failed bulks: {0} ({1} documents)".format(failed_bulks, (failed_bulks * NUMBER_OF_METRICS_PER_BULK)))
    print("Indexed approximately {0} MBs in {1} secconds".format(size_mb, elapsed_time))
    print("{0:.2f} MB/bulk".format(mbs_per_bulk))
    print("{0:.2f} MB/s".format(mbs_per_sec))
    print("{0:.2f} docs/s".format(doc_per_sec))
    print("")


    if isFinal:
        # clear file content, but also clear the other test cases
        # open('report.txt', 'w').close()
        # begin report
        report_file = open('report.txt', 'a')
        report_file.write("------------------------------------\n")
        report_file.write("Test case of clients number={0} is done! Final results:\n".format(NUMBER_OF_CLIENTS))
        report_file.write("------------------------------------\n")
        report_file.write("Clients number: {0}  \n".format(NUMBER_OF_CLIENTS))
        report_file.write("Elapsed time: {0} seconds \n".format(elapsed_time))
        report_file.write("Successful bulks: {0} ({1} documents \n)".format(success_bulks, (success_bulks * NUMBER_OF_METRICS_PER_BULK)))
        report_file.write("Failed bulks: {0} ({1} documents \n)".format(failed_bulks, (failed_bulks * NUMBER_OF_METRICS_PER_BULK)))
        report_file.write("Indexed approximately {0} MBs in {1} secconds \n".format(size_mb, elapsed_time))
        report_file.write("{0:.2f} MB/bulk \n".format(mbs_per_bulk))
        report_file.write("{0:.2f} MB/s \n".format(mbs_per_sec))
        report_file.write("{0:.2f} docs/s".format(doc_per_sec))
        report_file.write("\n")
        report_file.write("\n")
        report_file.close()

def print_stats_worker(NUMBER_OF_CLIENTS):

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
            print_stats(NUMBER_OF_CLIENTS, False)
