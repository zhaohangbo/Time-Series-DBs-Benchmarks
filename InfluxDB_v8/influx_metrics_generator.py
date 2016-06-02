import argparse
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
import datetime
import random
import json
import sys
# multiple points with the same timestamp and different values


def get_batch(batch_size=1000, series_name="benchmark_series", client_tag="client_x"):
    now = datetime.datetime.today()

    series = []
    series_total_physical_size = 0
    batch_str = ""
    for i in range(0, batch_size):
        past_date = now - datetime.timedelta(minutes=i)
        filed_value = random.randint(0, 200)

        pointValues = {
                    "name": series_name,
                    "columns": ["time",
                                "filed_value",
                                "client_tag"
                                ],
                    "points": [
                              [int(past_date.strftime('%s')),
                               filed_value,
                               client_tag
                               ]
                    ]
                }
        batch_str += json.dumps(pointValues)
        series_total_physical_size += sys.getsizeof(str(batch_str))
        series.append(pointValues)
    return series, series_total_physical_size
