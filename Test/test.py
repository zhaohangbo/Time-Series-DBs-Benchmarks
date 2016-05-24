import string
from random import randint, choice
# For json operations
import json
import sys
import random
import ES.benchmark_helper

# https://elasticsearch-py.readthedocs.io/en/master/
from datetime import datetime

# Just to control the minimum value globally (though its not configurable)
from itertools import islice, cycle
import numpy

types = ["long_metrics",
         "integer_metrics",
         "short_metrics",
         "byte_metrics",
         "double_metrics",
         "float_metrics",
         "boolean_metrics"]

mappings_body = {
        "_default_": {
              "dynamic_templates": [
                    {
                      "strings": {
                        "match": "*",
                        "match_mapping_type": "string",
                        "mapping":   { "type": "string",  "doc_values": True, "index": "not_analyzed" }
                      }
                    }
                ],
                "_all":            { "enabled": False},
                "_source":         { "enabled": False},
                "properties": {
                    "@timestamp":  { "type": "date",    "doc_values": True}
                }
        },
        "long_metrics": {
              "properties": {
                "long_value":    { "type": "long",    "doc_values": True, "index": "no"}
              }
        },
        "integer_metrics": {
              "properties": {
                "integer_value": { "type": "integer", "doc_values": True, "index": "no"}
              }
        },
        "short_metrics": {
              "properties": {
                "short_value":   { "type": "short",   "doc_values": True, "index": "no"}
              }
        },
        "byte_metrics": {
              "properties": {
                "byte_value":    { "type": "byte",    "doc_values": True, "index": "no"}
              }
        },
        "double_metrics": {
              "properties": {
                "double_value":  { "type": "double",  "doc_values": True, "index": "no"}
              }
        },
        "float_metrics": {
              "properties": {
                "float_value":   { "type": "float",   "doc_values": True, "index": "no"}
              }
        },
        "boolean_metrics": {
              "properties": {
                "boolean_value": { "type": "boolean", "doc_values": True, "index": "no"}
              }
        }
}

def generate_random_int(max_size):

    try:
        return randint(1, max_size)
    except:
        print("Not supporting {0} as valid sizes!".format(max_size))
        sys.exit(1)

# Generate a random string with length of 1 to provided param
def generate_random_string(max_size):

    return ''.join(choice(string.ascii_lowercase) for _ in range(5))


# Generate doc with random numder of fields
def generate_document():

    temp_doc = {}

    # Iterate over the max fields
    # the loop variable '_' isn't actually used.
    for _ in range(generate_random_int(12)):

        # Generate a field, with random content
        temp_doc[generate_random_string(10)] = generate_random_string(12)

    # Return the created document
    return temp_doc

def generate_float_metric():
    float_metric = {}

    random_float = random.uniform(0, 1000000);

    float_metric["@timestamp"] = datetime.now()
    float_metric["value"]      = random_float

    # Return the metric with a random value
    return float_metric


def roundrobin(*iterables):
    "roundrobin(['A1','B1'], ['C1'], ['D1','F1']) --> A1 C1 D1 B1 F1"
    # Recipe credited to George Sakkis
    pending = len(iterables)  # pending means num of no-empty iterables left
    nexts = cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                a = next()
                print(pending, a)
                yield a
        except StopIteration:
            pending -= 1
            print('=====', pending)
            nexts = cycle(islice(nexts, pending))

if __name__=="__main__":
    for type_name in types:
        print mappings_body[type_name]
    # print (sys.maxint, -sys.maxint-1)
    # a = int('1111111111111111111111111111111111111111111111111111111111111111', 2)
    # b = int('0111111111111111111111111111111111111111111111111111111111111111', 2)
    # c = -int('0111111111111111111111111111111111111111111111111111111111111111', 2)
    # print a
    # print(b, c)
    #
    #
    # if bool(random.getrandbits(1)):
    #     print numpy.float32(random.getrandbits(32))
    # else:
    #     print - numpy.float32(random.getrandbits(32))  # numpy.float32()


    # if bool(random.getrandbits(1)):
    #     print random.getrandbits(8-1)
    # else:
    #     print - random.getrandbits(8-1)
    # if bool(random.getrandbits(1)):
    #     print random.getrandbits(2)    # max , +3
    # else:
    #     print - random.getrandbits(2)  # min , -3

    # print numpy.iinfo(numpy.int64).min
    # print numpy.iinfo(numpy.int64).max
    # print numpy.iinfo(numpy.uint64).min
    # print numpy.iinfo(numpy.uint64).max
    # print numpy.iinfo(numpy.int32).min
    # print numpy.iinfo(numpy.int32).max
    # print numpy.iinfo(numpy.uint32).min
    # print numpy.iinfo(numpy.uint32).max

    # print numpy.finfo(numpy.float64).max
    # print numpy.finfo(numpy.float64).min
    # print numpy.finfo(numpy.float32).max
    # print numpy.finfo(numpy.float32).min

    # float64_MAX = numpy.finfo(numpy.float64).max
    # float64_MIN = numpy.finfo(numpy.float64).min
    # float32_MAX = numpy.finfo(numpy.float32).max
    # float32_MIN = numpy.finfo(numpy.float32).min
    # Won't work
    # random_float = random.uniform(float64_MIN, float64_MAX)
    # random_float = random.uniform(float32_MIN, float32_MAX)
