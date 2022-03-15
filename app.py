from flask import Flask, render_template
from turbo_flask import Turbo
import threading
import time


app = Flask(__name__)
turbo = Turbo(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.context_processor
def inject_data():
    with open('./found_devices.txt', 'rt') as f:
        data = []
        for line in f:
            temp = line.split('/')
            data.append(temp)
    return {'devices': data}

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