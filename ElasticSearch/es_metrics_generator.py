import random
from datetime import datetime
import sys
import json
from random import choice

types = ["long_metrics",
         "integer_metrics",
         "short_metrics",
         "byte_metrics",
         "double_metrics",
         "float_metrics",
         "boolean_metrics"]

metrics_pool_dict = {
        'long_metrics':    [],
        'integer_metrics': [],
        'short_metrics':   [],
        'byte_metrics':    [],
        'double_metrics':  [],
        'float_metrics':   [],
        'boolean_metrics': []
        }

bulks_pool = []  # [[bulk_str,size], [bulk_str,size]], default length 10

NUMBER_OF_METRICS_PER_BATCH = 0
index_names = []

def init(_NUMBER_OF_METRICS_PER_BATCH, _indices):
    global NUMBER_OF_METRICS_PER_BATCH
    global index_names
    NUMBER_OF_METRICS_PER_BATCH = _NUMBER_OF_METRICS_PER_BATCH
    index_names = _indices


def generate_bulk(NUMBER_OF_METRICS_PER_BATCH=1000, indices=[]):

    cur_bulk = ""
    for i in range(NUMBER_OF_METRICS_PER_BATCH):
        #Randomly pick a type
        type_name = choice(types)

        # Generate the bulk operation, here {0} means the 0-th argument
        cur_bulk += "{0}\n".format(json.dumps({"index": {"_index": choice(indices), "_type": type_name}}))
        cur_bulk += "{0}\n".format(json.dumps(choice(metrics_pool_dict[type_name])))

    bulk_total_physical_size = sys.getsizeof(str(cur_bulk))
    return cur_bulk, bulk_total_physical_size


def fill_bulks_pool():

    global bulks_pool
    for _ in range(10):
        cur_bulk, bulk_total_physical_size = generate_bulk(NUMBER_OF_METRICS_PER_BATCH, index_names)
        bulks_pool.append([cur_bulk, bulk_total_physical_size])


def fill_metrics_pool():
    global metrics_pool_dict
    for key in metrics_pool_dict.iterkeys():
        metrics_pool_dict[key] = []

    for _ in range(30):
        for key in metrics_pool_dict.iterkeys():
            # To help understand
            # long_pool.append(get_metric_by_type_name("long_metrics"))
            metrics_pool_dict[key].append(get_metric_by_type_name(key))


# In one Index, all types share one same Mapping
# So if a same key_name appears in all the 3 types,
# we can not map Integer,Long,Boolean to key_name at the same time, although key_name belongs to different 3 types
# Solution: we should use different key_names.
def get_metric_by_type_name(type_name):
    a_metric = {}
    a_metric["@timestamp"] = datetime.now().isoformat()

    key_name = None
    random_value = None

    if type_name == "long_metrics":
        key_name =  "long_value"
        if bool(random.getrandbits(1)):
            random_value = random.getrandbits(63)
        else:
            random_value = - random.getrandbits(63)

    if type_name == "integer_metrics":
        key_name =  "integer_value"
        if bool(random.getrandbits(1)):
            random_value = random.getrandbits(31)
        else:
            random_value = - random.getrandbits(31)

    if type_name == "short_metrics":
        key_name =  "short_value"
        if bool(random.getrandbits(1)):
            random_value = random.getrandbits(15)
        else:
            random_value = - random.getrandbits(15)

    if type_name == "byte_metrics":
        key_name =  "byte_value"
        if bool(random.getrandbits(1)):
            random_value = random.getrandbits(7)
        else:
            random_value = - random.getrandbits(7)

    # I haven't had a good idea to generate a random es-double(float64) covering the whole double range
    # But it doesn't matter for the performance test, we can define the type as double in es-mapping first
    if type_name == "double_metrics":
        key_name =  "double_value"
        random_value = random.uniform(0, 1000000)

    # I haven't had a good idea to generate a random es-float(float32) covering the whole float range
    # But it doesn't matter for the performance test, we can define the type as float in es-mapping first
    if type_name == "float_metrics":
        key_name =  "float_value"
        random_value = random.uniform(0, 1000000)

    if type_name == "boolean_metrics":
        key_name =  "boolean_value"
        random_value = bool(random.getrandbits(1))

    if key_name is None or random_value is None:
        raise Exception("Can't get_metric_by_type_name")

    a_metric[key_name] = random_value
    return a_metric
