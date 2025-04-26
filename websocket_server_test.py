from flask import Flask
from flask_sock import Sock

app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace_me_with_secret'
sock = Sock(app)



@sock.route('/hi')
def handle_message(ws):
    while True:
        msg = ws.receive()
        if msg is None:
            break
        print(f"Received: {msg}")
        ws.send(f"Server says: {msg}")

@app.route('/')
def index():
    return "Flask-SocketIO server running on / for WebSockets and HTTP!"

if __name__ == "__main__":
    app.run(host='localhost', port=8000)
