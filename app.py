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

    for path, ifaces in objs.items():
        if DEVICE_INTERFACE in ifaces.keys():
            # print(ifaces[DEVICE_INTERFACE])
            # print("-----------------------")
            temp = {}
            temp['path'] = path
            temp['alias'] = ifaces[DEVICE_INTERFACE]['Alias']
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
            if 'UUIDs' in ifaces[DEVICE_INTERFACE]:
                temp['uuid'] = []
                for uuid in ifaces[DEVICE_INTERFACE]['UUIDs']:
                    temp['uuid'].append(uuid)
            if 'AddressType' in ifaces[DEVICE_INTERFACE]:
                temp['address_type'] = ifaces[DEVICE_INTERFACE]['AddressType']
            if 'Trusted' in ifaces[DEVICE_INTERFACE]:
                temp['trusted'] = ifaces[DEVICE_INTERFACE]['Trusted']
            if 'Blocked' in ifaces[DEVICE_INTERFACE]:
                temp['blocked'] = ifaces[DEVICE_INTERFACE]['Blocked']
            if 'Paired' in ifaces[DEVICE_INTERFACE]:
                temp['paired'] = ifaces[DEVICE_INTERFACE]['Paired']
            if 'LegacyPairing' in ifaces[DEVICE_INTERFACE]:
                temp['legacy_pairing'] = ifaces[DEVICE_INTERFACE]['LegacyPairing']
            if 'ServicesResolved' in ifaces[DEVICE_INTERFACE]:
                temp['services_resolved'] = ifaces[DEVICE_INTERFACE]['ServicesResolved']
            if 'TxPower' in ifaces[DEVICE_INTERFACE]:
                temp['tx_power'] = ifaces[DEVICE_INTERFACE]['TxPower']

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