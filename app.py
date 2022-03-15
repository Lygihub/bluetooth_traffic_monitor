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

def found_devices():
    DEVICE_INTERFACE = "{}.Device1".format(SERVICE_NAME)
    objs = mngr.GetManagedObjects()
    devices = []
    for path, interfaces in objs.items():
        if DEVICE_INTERFACE in interfaces.keys():
            data = interfaces[DEVICE_INTERFACE]
            temp = {}
            temp['time'] = datetime.now().strftime("%H:%M:%S"),
            if 'Address' in data:
                temp['mac'] = data['Address']
            # if 'ManufacturerData' in data:
            #     for k, v in data["ManufacturerData"].items():
            #         if k in temp.manufacturer_data:
            #             temp.manufacturer_data[k].append(v)
            #         else:
            #             temp.manufacturer_data[k] = [v]
                        
            #     vendors = list()
            #     for k in temp.manufacturer_data.keys():
            #         try:
            #             vendors.append(CompanyId(k).name)
            #         except ValueError:
            #             vendors.append(str(k))
            #     if len(vendors) > 0:
            #         vendor_str = "{}".format(", ".join(vendors))
            #     else:
            #         vendor_str = ""
            #     temp.vendor = vendor_str
            if 'RSSI' in data:
                temp['rssi'] = data['RSSI']

            devices.append(temp)

    return devices

@app.route('/')
def index():
    return render_template("index.html")

@app.context_processor
def inject_data():
    # devices = found_devices()
    with open('./found_devices.txt', 'rt') as f:
        devices = []
        for line in f:
            line = line.split('/')
            temp = {}
            temp['time'] = line[0]
            temp['mac'] = line[1]
            temp['vendor'] = line[2]
            temp['rssi'] = line[3]
            devices.append(temp)
    return {'devices': devices}

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