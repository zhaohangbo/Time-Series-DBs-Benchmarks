# Time Series DBs Stress Test

## Targets

1. ElasticSearch
2. InfluxDB
3. Kairosdb

## Benchmark ElasticSearch

#### Example(ElasticSearch Benchmark)

Run: 
```
cd ES/
./influx_singlenode_benchmark.py --host 10.10.10.12 --min_num_of_clients 1  --max_num_of_clients 3
./influx_singlenode_benchmark.py --host 10.10.10.12 --min_num_of_clients 1  --max_num_of_clients 3
```

Explain:
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

Run `./es_metrics_benchmark.py -h` to see all `Mandatory Parameters` and `Optional Parameters`:

#### Mandatory Parameters (ElasticSearch Benchmark)
| Parameter | Description |
| --- | --- |
| `min_num_of_clients` | The minimum number of threads that send bulks to ES(threads num will range from min_client_num to max_client_num) |
| `max_num_of_clients` | The maximum number of threads that send bulks to ES(threads num will range from min_client_num to max_client_num) |
| `running_seconds` | How long should the test run. Note: it might take a bit longer, cause current batch operation needs time to complete |

#### Optional Parameters (ElasticSearch Benchmark)
| Parameter       | Description |
| --- | --- |
| `--es-hosts`       | A list of IPs in the Elasticsearch cluster (no protocol and port, use default) |
| `--number-of-indices`       | Number of indices to write to (default 8) |
| `--number-of-shards`       | How many shards per index (default 3) |
| `--number-of-replicas`       | How many replicas per index (default 1) |
| `--number-of-metrics-per-bulk` | How many metric docs each bulk request should contain (default 600000)|
| `--cleanup`       | Boolean field. If Delete the indices after completion(default False) |
| `--stats-interval`       | Number of seconds to wait between stats prints (default 30), How frequent to show the statistics |


#### Idea (ElasticSearch Benchmark)

Step 1. Create N(number-of-indices) indices with the certain NUMBER_OF_SHARDS and NUMBER_OF_REPLICAS
```
settings_body = {"settings":
                     {
                         "number_of_shards":   NUMBER_OF_SHARDS,
                         "number_of_replicas": NUMBER_OF_REPLICAS,
                         "index": {"refresh_interval": str(REFRESH_INTERVAL)+"s"}
                     }
                 }
```

Step 2. Within each index, there are 7 metric types
```
types = ["long_metrics",
         "integer_metrics",
         "short_metrics",
         "byte_metrics",
         "double_metrics",
         "float_metrics",
         "boolean_metrics"]
```

Step 3. Put the mapping for each index with 7 metric typs
```
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
                "_all":            { "enabled": True},
                "_source":         { "enabled": True},
                "properties": {
                    "@timestamp":  { "type": "date",    "doc_values": True}
                }
        },
        "long_metrics": {
              "properties": {
                "long_value":    { "type": "long",    "doc_values": True}
              }
        },
        "integer_metrics": {
              "properties": {
                "integer_value": { "type": "integer", "doc_values": True}
              }
        },
        "short_metrics": {
              "properties": {
                "short_value":   { "type": "short",   "doc_values": True}
              }
        },
        "byte_metrics": {
              "properties": {
                "byte_value":    { "type": "byte",    "doc_values": True}
              }
        },
        "double_metrics": {
              "properties": {
                "double_value":  { "type": "double",  "doc_values": True}
              }
        },
        "float_metrics": {
              "properties": {
                "float_value":   { "type": "float",   "doc_values": True}
              }
        },
        "boolean_metrics": {
              "properties": {
                "boolean_value": { "type": "boolean", "doc_values": True}
              }
        }
}
```

Step 4. Generate Metrics_Pool in memory with 7 different metric types

```
metrics_pool_dict = {
        'long_metrics':    [],  # list.length = 20
        'integer_metrics': [],
        'short_metrics':   [],
        'byte_metrics':    [],
        'double_metrics':  [],
        'float_metrics':   [],
        'boolean_metrics': []
        }

When forming a bulk, we randomly pick one metric from this metrics_pool, as following:
cur_bulk += "{0}\n".format(json.dumps( choice(metrics_pool_dict[type_name])) )
```

Step 5. Set the Size of Per Bulk
```
The physical size of the bulk that is more important than the document count.
Start with a bulk size around 5-15 MB and slowly increase it until no performance gains any more.
By default, `--number-of-metrics-per-bulk = 60000, at which the physical size per Bulk is 6-8 MB`
```

Step 6. Concurrency
```
Use `min_num_of_clients` and `max_num_of_clients` parameters to define the range of thread number.
Then start increasing the concurrency of your bulk ingestion (multiple threads, etc)
```

Step 7. View `report.txt` and find where `number of Failed bulks > 0`

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

Step 8. Round-Robin
```
By default round-robin strategy is used by the ES-PY Api for load balancing.
```

Step 9. Marvel Plugin & EsRejectedExecutionException
```
Monitor your nodes with Marvel or tools like isolate, top, and ps to see the bottleneck of resources.
If you start to receive EsRejectedExecutionException,
Then your cluster is at-capacity with some resource and you need to reduce concurrency
```


## Benchmark InfluxDB v0.8

This benchmark is targeted at the InfluxDB v0.8.8, which is compatible with Grafana 1.9.1

### Install or upgrade python client(InfluxDB v0.8 Benchmark)
```
$ sudo pip install influxdb
$ sudo pip install --upgrade influxdb
```

#### Example(InfluxDB v0.8 Benchmark)

Run:
```
cd InfluxDB_v8/
./influx_singlenode_benchmark.py --min_num_of_clients 1 --max_num_of_clients 2 --host 10.10.10.12
```

Explain:
```
In this case, we do influx_singlenode_benchmark with the following parameters:
min_num_of_clients = 1,
max_num_of_clients = 2,
host = 10.10.10.12

running_seconds = default, which is 60 secs
batch_size = default, which is 1000

which means,
Range the number of clients from 1(min_num_of_clients) to 2(max_num_of_clients);
Run each test case with a specific num_of_clients
See what performance we will get.
```

Run `./influx_singlenode_benchmark.py -h` to see all the `Optional Parameters`:

#### Optional Parameters (InfluxDB v0.8 Benchmark)
| Parameter           | Description |
| ---- | ---- |
|  `--host`           | Hostname influxdb http API (default, localhost) |
|  `--port`           | Port influxdb http API (default 8086) |
|  `--batch_size`     | Number of metrics per batch, limited ,can not be too big |
|  `--min_num_of_clients`     | The minimum number of threads that send batchs to Influx(threads num will range from min_client_num to max_client_num) |
|  `--max_num_of_clients`     | The maximum number of threads that send batchs to Influx(threads num will range from min_client_num to max_client_num) |
|  `--running_seconds`        | How long should the test run. Note: it might take a bit longer, cause current batch operation needs time to complete |
|  `--stats-interval`         | Number of seconds to wait between stats prints (default 30s), How frequent to show the statistics |


#### Idea (InfluxDB v0.8 Benchmark)

Step 1. Greate Database

Step 2. Run multiple clients and do batch writes

Step 3. Drop Database

Step 4. View `report.txt` and find where `number of Failed bulks > 0`

```
------------------------------------
Test case of clients number=1 is done! Final results:
------------------------------------
Clients number: 1  
Elapsed time: 61 seconds 
Successful bulks: 37 (37000 metrics )
Failed bulks: 0 (0 metrics )
Indexed approximately 2004 MBs in 61 secconds 
54.16 MB/batch 
32.85 MB/s 
606.56 docs/s

------------------------------------
Test case of clients number=2 is done! Final results:
------------------------------------
Clients number: 2  
Elapsed time: 61 seconds 
Successful bulks: 81 (81000 metrics )
Failed bulks: 0 (0 metrics )
Indexed approximately 4388 MBs in 61 secconds 
54.17 MB/batch 
71.93 MB/s 
1327.87 docs/s

------------------------------------
Test case of clients number=3 is done! Final results:
------------------------------------
Clients number: 3  
Elapsed time: 60 seconds 
Successful bulks: 126 (126000 metrics )
Failed bulks: 0 (0 metrics )
Indexed approximately 6827 MBs in 60 secconds 
54.18 MB/batch 
113.78 MB/s 
2100.00 docs/s
```


## Benchmark KairosDB

## Contribution
You are more then welcome!
Please open a PR or issues here.
