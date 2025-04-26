from flask import Flask, render_template

app = Flask(__name__)

@app.route('/stations')
def stations():
    return render_template('stations.html')

@app.route('/')
def users():
    return render_template('users.html')

if __name__ == '__main__':
    app.run(debug=True)
