from flask import Flask, jsonify, request
from pipelines import pipelines

app = Flask(__name__)

frequency = None
last_keep_alive = None

snr = 0
rssi = 0


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



def start_sdr():
    # Placeholder for starting the SDR
    pass


def stop_sdr():
    # Placeholder for stopping the SDR
    pass


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
