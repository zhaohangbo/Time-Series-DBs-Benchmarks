
InfluxDB Version: v0.8.8

InfluxDB Host and Port: 10.10.10.12:8083

Configure Grafana 1.9.1

```
vim config.js
      datasources: {
        influxdb: {
          type: 'influxdb',
          url: "http://10.10.10.12:8086/db/collectd_db",
          username: 'root',
          password: 'root',
        },
        grafana: {
          type: 'influxdb',
          url: "http://10.10.10.10:8086/db/grafana",
          username: 'admin',
          password: 'admin',
          grafanaDB: true
        },
      },
```

InfluxDB Installation
https://docs.influxdata.com/influxdb/v0.8/introduction/installation/

Collectd and InfluxDB Config
https://anomaly.io/collectd-metrics-to-influxdb/


# Time Series DBs Stress Test

## Targets

1. ElasticSearch
2. InfluxDB
3. Kairosdb

## Benchmark InfluxDB v0.8

This benchmark is targeted at the InfluxDB v0.8.8, which is compatible with Grafana 1.9.1.

### Install or upgrade python client for InfluxDB
```
$ sudo pip install influxdb
$ sudo pip install --upgrade influxdb
```

#### Example:

Run:
```
cd InfluxDB_v8/
./es_metrics_benchmark.py 1 2 60 --number-of-metrics-per-bulk 60000
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

#### Optional Parameters (InfluxDB v0.8)
| Parameter       | Description |
| --- | --- |
| `--host`       | Hostname influxdb http API (default, localhost) |
| `--port`       | Port influxdb http API (default 8086) |
| `--batch_size` | Number of metrics per batch, limited ,can not be too big |
| `--min_num_of_clients` | The minimum number of threads that send bulks to ES(threads num will range from min_client_num to max_client_num) |
| `--max_num_of_clients` | The maximum number of threads that send bulks to ES(threads num will range from min_client_num to max_client_num) |
| `--running_seconds`    | How long should the test run. Note: it might take a bit longer, as sending of all bulks who's creation has been initiated is allowed |
| `--stats-interval`     | Number of seconds to wait between stats prints (default 30), How frequent to show the statistics |


#### Idea (InfluxDB Benchmark)

Step 1. Greate Database

Step 2. Run multiple clients and do batch writes

Step 3. Drop Database

Step 4. View your stress test report with a certain thread number range


## Contribution
You are more then welcome!
Please open a PR or issues here.

