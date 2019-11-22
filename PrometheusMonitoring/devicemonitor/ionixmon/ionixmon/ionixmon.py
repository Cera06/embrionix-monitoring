# Copyright 2019 Embrionix Design Inc.
#
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


from flask import Flask, render_template, flash, request, send_file
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import logging
import docker
docker_client = docker.from_env()
app = Flask(__name__)

monitored_devices = []

class MonitoringInformation():
    def __init__(self, ip, prettyName):
        self.ip = ip
        self.prettyName = prettyName


# Static file serving...  To allow Ionixmon usage without internet access...
@app.route('/js/jquery-3.3.1.slim.min.js')
def send_jquery():
    return send_file('js/jquery-3.3.1.slim.min.js')


@app.route('/js/popper.min.js')
def send_popper():
    return send_file('js/popper.min.js')


@app.route('/js/bootstrap.min.js')
def send_bootstrapjs():
    return send_file('js/bootstrap.min.js')


@app.route('/css/bootstrap.min.css')
def send_bootstrapcss():
    return send_file('css/bootstrap.min.css')


@app.route('/', methods=['GET', 'POST'])
def MainPage():
    name = TextField('Name:', validators=[validators.required()])
    app.logger.warning(str(request.form))
    if request.method == 'POST' and "addDevice" in request.form:
        deviceIp = request.form['deviceIp']
        deviceName = request.form['deviceName']
        newDev = MonitoringInformation(deviceIp, deviceName)
        monitored_devices.append(newDev)
        app.logger.warning("Device IP: " + str(newDev.ip) + " Device name: " + str(newDev.prettyName))
        docker_client.containers.run("prometheus_interface", 
            environment = ["deviceip="+deviceIp, "port=10600", "prettyName="+deviceName], 
            name=deviceName,
            detach=True, 
            volumes={'graphicmonitor_to_monitor': {'bind': '/home/to_monitor/', 'mode': 'rw'}}, 
            publish_all_ports=True,
            network="graphicmonitor_bridge_net")
        return render_template('index.html', monitoredDevices=monitored_devices)
    elif request.method == 'POST' and "viewDevices" in request.form:
        return render_template('view_monitored_devices.html', monitoredDevices=monitored_devices)
    elif request.method == 'POST' and "viewGraphs" in request.form:        
        return render_template('view_graphs.html', monitoredDevices=monitored_devices)
    elif request.method == 'POST' and "viewContainer" in request.form: 
        containerId = request.form['containerId']
        containerObj = docker_client.containers.get(containerId)
        app.logger.warning("obj=" + str(containerObj))
        app.logger.warning("objdir=" + str(dir(containerObj)))
        app.logger.warning("container id: " + str(containerId))
        app.logger.warning("container log: " + str(containerObj.logs()))
        return render_template('view_docker_status.html', containerId=containerId, containerLog=containerObj.logs(stdout=True, stderr=True))
    else:
        app.logger.warning("Got: " + str(request.method))
        return render_template('index.html', monitoredDevices=monitored_devices)



if __name__ == '__main__':
    image_id = docker_client.images.get("prometheus_interface:latest").id
    for container in docker_client.containers.list():

        if container.image.id == image_id:
            devIp = None
            env = container.attrs["Config"]["Env"]
            for kv in env:
                key = kv.split("=")[0]
                if key == "deviceip":
                    devIp = kv.split("=")[1]
            if devIp is not None:
                app.logger.warning("Adding an already present monitor container: " + container.name)
                newDev = MonitoringInformation(devIp, container.name)
                monitored_devices.append(newDev)
            else:
                app.logger.warning("Could not add container: " + container.name)

    app.run(host='0.0.0.0', port=8060)
