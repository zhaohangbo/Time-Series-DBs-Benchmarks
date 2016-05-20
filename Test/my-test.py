import string
from random import randint, choice
# For json operations
import json
import sys
import random

# https://elasticsearch-py.readthedocs.io/en/master/
from datetime import datetime

# Just to control the minimum value globally (though its not configurable)
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

    float_metric["@timestamp"] =datetime.now()
    float_metric["value"]      =random_float

    # Return the metric with a random value
    return float_metric

def main():
    #a =str(generate_random_string)
    print ''.join(choice(string.ascii_lowercase))


    document =generate_document();
    print document

    curr_bulk  =""
    curr_bulk += "{0}\n".format(json.dumps({"index": {"_index": "my-index", "_type": "stresstest"}}))
    curr_bulk += "{0}\n".format(json.dumps(document))

    print "====================="
    print curr_bulk

if __name__ == "__main__":

    sth =generate_float_metric()
    # print type(sth)
    # cur_bulk = "{0}\n".format(json.dumps())
    # print cur_bulk
    isinstance(sth, datetime.datetime)
    # print random.uniform(0, 1000000);
    #stra="a"
    # stra+="aa"
    # print "aaa"==stra
  # main()
