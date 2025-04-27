from flask import Flask, redirect, render_template, request, url_for,abort
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
    register_sdr_bd,
    update_station_info,
    check_api_key,
    update_api_key
    
)
import requests



#init_bd()
#populate_base_data()

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
    if confirm_ownership(current_user.id,id):
        change_button = True
    if request.method == "GET":
        owner = get_station_owner(id)
        info = get_full_station_info_by_id(id)
    return render_template("stations.html", owner=owner,info=info, change_button=change_button)


@app.route("/stations/<id>/dashboard", methods=["GET", "POST"])
@login_required
def station_dashboard(id):
    user_id = current_user.id
    if confirm_ownership(current_user.id,id):
        info = []
        print(confirm_ownership(current_user.id,id))
        stations_id = get_stations_by_user_id(user_id)
        for id in stations_id:
            ex = get_station_brief_info_by_id(id)
            info.append(ex)

        name = get_station_brief_info_by_id(id)[1]
    else:
        return abort(403)
    return render_template("dashboard.html", station_id=id,name=name,user_stations=info)


@app.route("/stations/<id>/dashboard/map", methods=["GET", "POST"])
@login_required
def map(id):
    if request.method == "GET":
        info = get_full_station_info_by_id(id)
        station_planned_tles = requests.get(
            f"https://sonik.space/api/jobs/?id=&status=&ground_station={id}"
        )
        tles = []
        print(station_planned_tles.json)
        for i in station_planned_tles.json:
            res = {}
            res["tle0"] = i["tle0"]
            res["tle1"] =i["tle1"]
            res["tle2"] = i["tle2"]
            stat_inf = get_full_station_info_by_id(id)
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
        info = request.json
        mail = info["notify_mail"]
        tg = info["notify_tg"]
        time = info["early_time"]
        key = info["api_key"]
        update_station_info(
            id, notify_mail=mail, notify_tg=tg, early_time=time)
        if key!='':
            update_api_key(current_user.id,key)

    return render_template("settings.html", info=info)




@app.route("/stations/<id>/register_sdr", methods=["GET", "POST"])
@login_required
def register_sdr(id):
    if request.method == "GET":
        sdr = request.args.get('address')
        key = request.args.get('key')
        print(sdr)
        if sdr and check_api_key(key,id):
            register_sdr_bd(id,sdr)
            return {"Status":"Ok"}
        else:
            return {"Status":"Fail"}

@app.route("/stations/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_station(id):
    if request.method == "GET":
        info = get_full_station_info_by_id(id)
    if request.method == "POST":
        info = request.json
        name = info["name"]
        lat = info["lat"]
        long = info["long"]
        alt = info["alt"]
        update_station_info(
            id,
            name=name,
            lat=lat,
            long=long,
            alt=alt,
        )
        return redirect(url_for("satation", id=id))

    return render_template("stations_editor.html", info=info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
