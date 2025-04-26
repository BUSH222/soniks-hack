from flask import Flask, jsonify, request
from pipelines import pipelines
import time
import threading

app = Flask(__name__)

frequency = None
last_keep_alive = None
KEEP_ALIVE_TIMEOUT = 30  # seconds
snr = 0
rssi = 0


def check_keep_alive():
    global last_keep_alive
    while True:
        current_time = time.time()
        print("Checking keep alive, time since last keep alive:",
              current_time - last_keep_alive if last_keep_alive else "Never")
        if last_keep_alive and (current_time - last_keep_alive > KEEP_ALIVE_TIMEOUT):
            stop_sdr()
            last_keep_alive = None
        time.sleep(10)


@app.route('/start_conn', methods=['POST'])
def start_conn():
    frequency = request.args.get('frequency')
    assert frequency is not None, "Frequency parameter is required"
    assert frequency.isdigit(), "Frequency must be a number"
    frequency = int(frequency)
    # Placeholder for starting the SDR
    return jsonify(pipelines), 200


@app.route('/change_freq', methods=['GET'])
def change_freq():
    frequency = request.args.get('frequency')
    assert frequency is not None, "Frequency parameter is required"
    assert frequency.isdigit(), "Frequency must be a number"
    frequency = int(frequency)
    return 'ok', 200


@app.route('/keep_alive', methods=['GET', 'POST'])
def keep_alive():
    global last_keep_alive
    last_keep_alive = time.time()
    return jsonify({"snr": snr, "rssi": rssi}), 200


def stop_sdr():
    # Placeholder for stopping the SDR
    pass


if __name__ == '__main__':
    threading.Thread(target=check_keep_alive, daemon=True).start()
    app.run(debug=True, use_reloader=False)
