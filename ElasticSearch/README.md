# Time Series DBs Stress Test

## Targets

1. ElasticSearch
2. InfluxDB
3. Kairosdb

## Benchmark ElasticSearch

Example:

Run: `cd ES/`

Run: `./es_metrics_benchmark.py 1 2 60 --number-of-metrics-per-bulk 60000`

```
In this case, we do es_metrics_benchmark with the following parameters:
min_num_of_clients = 1,
max_num_of_clients = 2,
running_seconds = 60,
number-of-metrics-per-bulk = 60000,

which means,
Range the number of clients from 1(min_num_of_clients) to 2(max_num_of_clients);
Use number-of-metrics-per-bulk = 60000, which can ensure the physical size of the bulk is about 6-8 MB;
Set the running_seconds for each benchmark case with a certain thread number(num_of_clients).
```

To see all `Mandatory Parameters` and `Optional Parameters`:

Run `./es_metrics_benchmark.py -h`


#### Mandatory Parameters (ElasticSearch)
| Parameter | Description |
| --- | --- |
| `min_num_of_clients` | The minimum number of threads that send bulks to ES(threads num will range from min_client_num to max_client_num) |
| `max_num_of_clients` | The maximum number of threads that send bulks to ES(threads num will range from min_client_num to max_client_num) |
| `running_seconds` | How long should the test run. Note: it might take a bit longer, as sending of all bulks who's creation has been initiated is allowed |

#### Optional Parameters (ElasticSearch)
| Parameter       | Description |
| --- | --- |
| `--es-hosts`       | A list of IPs in the Elasticsearch cluster (no protocol and port, use default) |
| `--indices`       | Number of indices to write to (default 8) |
| `--number-of-shards`       | How many shards per index (default 3) |
| `--number-of-replicas`       | How many replicas per index (default 1) |
| `--number-of-metrics-per-bulk` | How many metric docs each bulk request should contain (default 1000)|
| `--cleanup`       | Boolean field. If Delete the indices after completion(default False) |
| `--stats-interval`       | Number of seconds to wait between stats prints (default 30), How frequent to show the statistics |


#### Idea (ElasticSearch Benchmark)

We use bulk indexing requests for optimal performance.

Obiviously, it’s the physical size of the bulk that is more important than the document count.

Step 1. Size Per Bulk
```
The physical size of the bulk that is more important than the document count.
Start with a bulk size around 5-15 MB and slowly increase it until no performance gains any more.
By default, `--number-of-metrics-per-bulk = 60000, at which the physical size per Bulk is 6-8 MB`
```

Step 2. Concurrency
```
Then start increasing the concurrency of your bulk ingestion (multiple threads, etc)
Use `min_num_of_clients` and `max_num_of_clients` parameters to define the range of thread number.
```

Step 3. View `report.txt` and find where `number of Failed bulks > 0`

```
Clients number: 1
Elapsed time: 62 seconds
Successful bulks: 10 (600000 documents)
Failed bulks: 0 (0 documents)
Indexed approximately 77 MBs in 62 secconds
7.70 MB/bulk
1.24 MB/s

Clients number: 2
Elapsed time: 31 seconds
Successful bulks: 17 (1020000 documents)
Failed bulks: 0 (0 documents)
Indexed approximately 131 MBs in 31 secconds
7.71 MB/bulk
4.23 MB/s

----------------------------
Test is done! Final results:
----------------------------
Clients number: 2
Elapsed time: 67 seconds
Successful bulks: 25 (1500000 documents)
Failed bulks: 0 (0 documents)
Indexed approximately 192 MBs in 67 secconds
7.68 MB/bulk
2.87 MB/s
```

Step 4. Round-Robin
```
By default round-robin strategy is used by the ES-PY Api for load balancing.
```

Step 5. Marvel Plugin & EsRejectedExecutionException
```
Monitor your nodes with Marvel or tools like isolate, top, and ps to see the bottleneck of resources.
If you start to receive EsRejectedExecutionException,
Then your cluster is at-capacity with some resource and you need to reduce concurrency
```


## Benchmark InfluxDB


## Benchmark KairosDB

## Contribution
You are more then welcome!
Please open a PR or issues here.