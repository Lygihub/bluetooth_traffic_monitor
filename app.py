from flask import Flask, render_template
from turbo_flask import Turbo
import pydbus
from src.hci_constants import CompanyId
import threading
import time
from datetime import datetime

app = Flask(__name__)
turbo = Turbo(app)
bus = pydbus.SystemBus()
# adapter = bus.get('org.bluez', '/org/bluez/hci0')
SERVICE_NAME = 'org.bluez'
mngr = bus.get(SERVICE_NAME, '/')

found_devices = []

def find_devices():
    DEVICE_INTERFACE = "{}.Device1".format(SERVICE_NAME)
    objs = mngr.GetManagedObjects()
    devices = []
    global found_devices

    for _, ifaces in objs.items():
        if DEVICE_INTERFACE in ifaces.keys():
            temp = {}
            temp['mac'] = ifaces[DEVICE_INTERFACE]['Address']
            for found_device in found_devices:
                if 'time' in found_device.keys():
                    if temp['mac'] == found_device['mac']:
                        temp['time'] = found_device['time']
                else:
                    temp['time'] = datetime.now().strftime("%H:%M:%S")
            if 'ManufacturerData' in ifaces[DEVICE_INTERFACE]:
                for k in ifaces[DEVICE_INTERFACE]['ManufacturerData'].keys():
                    temp['vendor'] = CompanyId(k).name
            else:
                temp['vendor'] = "Unknown"
            if 'RSSI' in ifaces[DEVICE_INTERFACE]:
                temp['rssi'] = ifaces[DEVICE_INTERFACE]['RSSI']
            devices.append(temp)
        
    return devices

@app.route('/')
def index():
    return render_template("index.html")

@app.context_processor
def inject_data():
    global found_devices
    devices = find_devices()
    found_devices = devices.copy()
    return {'devices': found_devices}

@app.before_first_request
def before_first_request():
    def update_found_device():
        with app.app_context():
            while True:
                time.sleep(1)
                turbo.push(turbo.replace(render_template('found_devices.html'), 'load'))
    threading.Thread(target=update_found_device).start()

if __name__ == "__main__":
    app.run(debug=True)