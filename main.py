from flask import Flask, redirect, render_template, request, url_for
from flask_login import (
    login_user,
    LoginManager,
    current_user,
    login_required,
    UserMixin,
    logout_user,
)
from bdinit import init_bd,populate_base_data
from dbmanager import (
    get_all_user_data_by_name,
    confirm_ownership,
    get_all_user_data_by_id,
    get_stations_by_user_id,
    get_user_id_by_name,
    get_station_brief_info_by_id,
    get_full_station_info_by_id,
    get_station_owner,
    update_station_info,
    
)
import requests


init_bd()
populate_base_data()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user_data = get_all_user_data_by_id(user_id)
    print(user_data)
    if user_data:
        return User(user_data[0],user_data[1],user_data[2])
    return None

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        username = data.get('username')
        password = data.get('password')
        user_data = get_all_user_data_by_name(username)
        print(user_data)
        if user_data:
            if user_data[2] == password and len(password) < 32:
                user = User(user_data[0],user_data[1],user_data[2])
                login_user(user)
                return 'OK'
            else:
                return "Invalid username or password"
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
def main():
    return render_template("login.html")


@app.route("/users/<name>", methods=["GET", "POST"])
@login_required
def user_stations(name):
    info = []
    if request.method == "GET":
        if current_user.username == name:
            user_id = get_user_id_by_name(name)
            stations_id = get_stations_by_user_id(user_id)
            print(f"id:{user_id}")
            print(f"stat:{stations_id}")
            for id in stations_id:
                ex = get_station_brief_info_by_id(id)
                info.append(ex)
                print(info)
        else:
            info = "Authification error"

    return render_template("users.html", stations=info)

@app.route("/stations/<id>", methods=["GET", "POST"])
@login_required
def station(id):
    if confirm_ownership(current_user.id, id):
        change_button = True
    if request.method == "GET":
        owner = get_station_owner(id)
        info = get_full_station_info_by_id(id)
    return render_template("stations.html", owner=owner,info=info, change_button=change_button)


@app.route("/stations/<id>/dashboard", methods=["GET", "POST"])
@login_required
def station_dashboard(id):
    return render_template("dashboard.html", id=id)


@app.route("/stations/<id>/dashboard/map", methods=["GET", "POST"])
@login_required
def map(id):
    if request.method == "GET":
        info = get_full_station_info_by_id(id)
        station_planned_tles = requests.get(
            f"/api/jobs/?id=&status=&ground_station={id}"
        )
        tles = []
        for i in station_planned_tles:
            res = {}
            res["tle0"] = station_planned_tles["tle0"]
            res["tle1"] = station_planned_tles["tle1"]
            res["tle2"] = station_planned_tles["tle2"]
            stat_inf = get_station_brief_info_by_id(id)
            res["lat"] = stat_inf[2]
            res["long"] = stat_inf[3]
            res["alt"] = stat_inf[4]
            tles.append(res)
    return render_template("stations_map.html", info=info, tles=tles)


@app.route("/stations/<id>/dashboard/reception", methods=["GET", "POST"])
@login_required
def reception(id):
    return render_template("reception.html", id=id)


@app.route("/stations/<id>/dashboard/archive", methods=["GET", "POST"])
@login_required
def archive(id):
    return render_template("archive.html", id=id)


@app.route("/stations/<id>/dashboard/settings", methods=["GET", "POST"])
@login_required
def settings(id):
    if request.method == "GET":
        info = get_station_brief_info_by_id(id)
    if request.method == "POST":
        mail = request.form["notify_mail"]
        tg = request.form["notify_tg"]
        time = request.form["early_time"]
        update_station_info(
            id, notify_mail=mail, notify_tg=tg, early_time=time)

    return render_template("settings.html", info=info)


@app.route("/stations/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_station(id):
    if request.method == "GET":
        info = get_full_station_info_by_id(id)
    if request.method == "POST":
        name = request.form["name"]
        lat = request.form["lat"]
        long = request.form["long"]
        alt = request.form["alt"]
        sdr_server_address = request.form["sdr_server_address"]
        update_station_info(
            id,
            name=name,
            lat=lat,
            long=long,
            alt=alt,
            sdr_server_address=sdr_server_address,
        )
        return redirect(url_for("satation", id=id))

    return render_template("stations_editor.html", info=info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
