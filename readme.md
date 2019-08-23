# Embrionix devices monitoring using Grafana and Prometheus

**Note: This is a proof of concept**

The monitor tool contains 3 major elements:
* emDeviceMonitor.py: Translate and expose Embrionix data to Prometheus format
* Prometheus: Datalogging server
* Grafana: Main UI

Prerequisites:
* Python 3.x (3.7 tested), libs: prometheus_client import, random, time, requests, argparse
* A running Docker instance
* Internet access for deployment (In order to fetch Docker images)	

Quickstart:
1. From the checkout folder (At the same level as the docker-compose.yml file), run 'sudo docker-compose up -d'.
1. Start a device monitor script, they are found under PrometheusMonitoring/devicemonitor, use emBox6Monitor.py for an EmBox6 and emBox3_2110sfp_Monitor.py for EmBox3 or other 2110 device, syntax for both is: python emDeviceMonitor.py --ip embox6_ip --port promtheus_interface_port
1. Copy file PrometheusMonitoring/server/sample_monitor.json, fill in information using your host ip on docker and the port specified on the monitor script.
1. Add your new file by copying it to the target container: docker cp <new_file.json> emprometheus:/home/to_monitor
1. Repeat the last two steps for each devices you want to monitor
1. Connect to prometheus target page on: http://127.0.0.1:9090/targets, verify that your target is up
1. Open Graphana on 127.0.0.1:3000 with a web browser (Default user/password is admin/admin)