# Elasticsearch Stress Test

### Overview
This script generates a bunch of docs(time-series-metrics), and indexes as much as it can to elasticsearch.
While doing so, it prints out metrics of the process to the screen to let you follow how your cluster is doing.

### How to use
* Save this script
* Make sure you have python 2.7+
* pip install elasticsearch

### How does indexing documents work
The script creates document templates based on your input. Say - 5 different documents.
The documents are created without fields, for the purpose of having the same mapping when indexing to ES.
After that, the script takes 10 random documents out of the template pool (with redraws) and populates them with random data.

After we have the pool of different documents, we select an index out of the pool, select documents * bulk size out of the pool, and index them.

*The generation of documents is being processed before the run, so it will not overload the server too much during the benchmark*

### Using and Sizing Bulk requests

```

Should be fairly obvious, but use bulk indexing requests for optimal performance.

Bulk sizing is dependent on your data, analysis and cluster configuration,
but a good starting point is 5-15 MB per bulk. Note that this is physical size.

Document count is not a good metric for bulk size.
For example ,if you are indexing 1000 documents per bulk:

     — 1000 docs at 1 KB each is l MB
     — 1000 docs at 100 KB each is 100 MB

Those are drastically different bulk sizes. Bulks need to be loaded into memory at the coordinating node,
so it’s the physical size of the bulk that is more important than the document count.

1. Size of Per Bulk, 5-15MB
   Start with a bulk size around 5-15 MB and slowly increase it until you do not see performance gains any more.

2. Concurrency
   Then start increasing the concurrency of your bulk ingestion (multiple threads, etc)

3. Marvel & EsRejectedExecutionException
   Monitor your nodes with Marvel and/or tools like isolate, top, and ps to see when resources start to bottleneck.
   If you start to receive EsRejectedExecutionException,
   Then your cluster is at-capacity with some resource and you need to reduce concurrency

4. Round-Robin
   When ingesting data, make sure bulk requests are round-robined actress all your data nodes.
   Do not send all requests to s single node, since that single node will need to store all the bulks in memory while processing

   By default round-robin strategy is used by the ES-PY Api for load balancing.
   https://elasticsearch-py.readthedocs.io/en/master/connection.html#elasticsearch.ConnectionPool
```

### Mandatory Parameters
| Parameter | Description |
| --- | --- |
| `number_of_clients` | Number of threads that send bulks to ES |
| `running_seconds` | How long should the test run. Note: it might take a bit longer, as sending of all bulks who's creation has been initiated is allowed |


### Optional Parameters
| Parameter | Description |
| --- | --- |
| `--es-hosts` | A list of IPs in the Elasticsearch cluster (no protocol and port, use default) |
| `--indices` | Number of indices to write to (default 8) |
| `--number-of-shards` | How many shards per index (default 3) |
| `--number-of-replicas` | How many replicas per index (default 1) |
| `--number-of-metrics-per-bulk` | How many metric docs each bulk request should contain (default 1000)|
| `--cleanup` | Boolean field. If Delete the indices after completion(default False) |
| `--stats-interval` | Number of seconds to wait between stats prints (default 30), How frequent to show the statistics |

### Contribution
You are more then welcome!
Please open a PR or issues here.