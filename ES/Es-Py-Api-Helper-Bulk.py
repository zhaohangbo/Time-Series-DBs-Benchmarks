from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch import helpers

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