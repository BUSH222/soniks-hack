from flask import Flask, redirect, render_template, request, url_for, abort, jsonify
from flask_login import (
    login_user,
    LoginManager,
    current_user,
    login_required,
    UserMixin,
    logout_user,
)
from bdinit import init_bd
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
    update_api_key,
    get_station_address_by_station_id,
    get_station_notif,
)
import requests
from beyond.io.tle import Tle
from beyond.dates import Date, timedelta
from beyond.frames import create_station
import numpy as np
from map import get_satellite_tracks_from_tle
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from matplotlib.figure import Figure
from matplotlib.patches import Circle
import os


init_bd()
# populate_base_data()

app = Flask(__name__)
app.secret_key = "your_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    user_data = get_all_user_data_by_id(user_id)
    print(user_data)
    if user_data:
        return User(user_data[0], user_data[1], user_data[2])
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
        username = data.get("username")
        password = data.get("password")
        user_data = get_all_user_data_by_name(username)
        print(user_data)
        if user_data:
            if user_data[2] == password and len(password) < 32:
                user = User(user_data[0], user_data[1], user_data[2])
                login_user(user)
                return "OK"
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
    return render_template(
        "stations.html", owner=owner, info=info, change_button=change_button
    )


@app.route("/stations/<id>/dashboard", methods=["GET", "POST"])
@login_required
def station_dashboard(id):
    user_id = current_user.id
    if confirm_ownership(current_user.id, id):
        info = []
        print(confirm_ownership(current_user.id, id))
        stations_id = get_stations_by_user_id(user_id)
        for id in stations_id:
            ex = get_station_brief_info_by_id(id)
            info.append(ex)

        name = get_station_brief_info_by_id(id)[1]
    else:
        return abort(403)
    return render_template(
        "dashboard.html", station_id=id, name=name, user_stations=info
    )


@app.route("/stations/<id>/dashboard/map", methods=["GET", "POST"])
@login_required
def map_thing(id):
    if request.method == "GET":
        return render_template("stations_map.html", station_id=id)
    elif request.method == "POST":
        station_planned_tles = requests.get(
            f"https://sonik.space/api/jobs/?id=&status=&ground_station={id}"
        )
        tles = []
        stat_inf = get_full_station_info_by_id(id)
        res = dict()
        res["lat"] = stat_inf[4]
        res["long"] = stat_inf[3]
        res["alt"] = int("".join(filter(str.isdigit, stat_inf[2].split()[1])))

        for i in station_planned_tles.json():
            added = False
            for tle in tles:
                if tle.split("\n")[0] == i["tle0"]:
                    added = True
                    break
            if not added:
                tles.append("\n".join([i["tle0"], i["tle1"], i["tle2"]]))

        tles = list(set(tles))[0:5]
        h1 = res["alt"]
        station_lat, station_long = res["lat"], res["long"]
        radius = np.sqrt(12756 * h1 + h1**2) + 2294

        # -----------------------------
        # 1) Generate the MAP figure
        # -----------------------------
        circle = Circle(
            (station_lat, station_long),
            radius / 150,
            color="yellow",
            alpha=0.3,
            label="Coverage Area",
        )
        circle2 = Circle(
            (station_lat, station_long), 1, color="blue", label="Station location"
        )
        fig_map = Figure(figsize=(15.2, 8.2))
        ax_map = fig_map.subplots()
        img = os.path.join(os.path.dirname(__file__), "image.png")
        im = plt.imread(str(img))
        ax_map.imshow(im, extent=[-180, 180, -90, 90])
        ax_map.add_patch(circle)
        ax_map.add_patch(circle2)

        for tle_str in tles:
            longitudes, latitudes, current_position = get_satellite_tracks_from_tle(tle_str)
            color = np.random.rand(3, )
            lon, lat = current_position
            for lons, lats in zip(longitudes, latitudes):
                ax_map.plot(lons, lats, color)
            ax_map.scatter(
                [lon], [lat],
                color=color,
                label=tle_str.split("\n")[0],
                s=50,
                edgecolors="black",
            )
        ax_map.set_xlim([-180, 180])
        ax_map.set_ylim([-90, 90])
        ax_map.grid(True, color="w", linestyle=":", alpha=0.4)
        ax_map.set_xticks(range(-180, 181, 30))
        ax_map.set_yticks(range(-90, 91, 30))
        ax_map.legend()
        fig_map.tight_layout()

        buf_map = BytesIO()
        fig_map.savefig(buf_map, format="png")
        buf_map.seek(0)
        map_data = base64.b64encode(buf_map.getbuffer()).decode("ascii")

        # -----------------------------
        # 2) Generate the POLAR figure
        # (sample code from your snippet)
        # -----------------------------
        # Example TLE
        iss_tle = Tle(tles[0]).orbit()
        tle_visual = (
            f"TLE Name: {iss_tle.tle.name}\n"
            f"Norad ID: {iss_tle.tle.norad_id}\n"
            f"Classification: {iss_tle.tle.classification}\n"
            f"Cospar ID: {iss_tle.tle.cospar_id}\n"
            f"Epoch: {iss_tle.tle.epoch}\n"
            f"Ndot: {iss_tle.tle.ndot}\n"
            f"Ndotdot: {iss_tle.tle.ndotdot}\n"
            f"Bstar: {iss_tle.tle.bstar}\n"
            f"Element Number: {iss_tle.tle.element_nb}\n"
            f"Revolutions: {iss_tle.tle.revolutions}\n"
            f"Inclination (i): {np.degrees(iss_tle.tle.i):.4f}°\n"
            f"RAAN (Ω): {np.degrees(iss_tle.tle.Ω):.4f}°\n"
            f"Eccentricity (e): {iss_tle.tle.e:.7f}\n"
            f"Argument of Perigee (ω): {np.degrees(iss_tle.tle.ω):.4f}°\n"
            f"Mean Anomaly (M): {np.degrees(iss_tle.tle.M):.4f}°\n"
            f"Mean Motion (n): {iss_tle.tle.n:.8f} rad/s\n"
        )

        # Create a station using the same lat/long/alt as above
        station = create_station("Station", (station_lat, station_long, float(h1)))
        azims, elevs = [], []

        start_time = Date.now()
        stop_time = start_time + timedelta(hours=24)
        step = timedelta(seconds=30)

        for orb in station.visibility(iss_tle, start=start_time, stop=stop_time, step=step, events=True):
            elev_deg = np.degrees(orb.phi)
            azim_deg = np.degrees(-orb.theta) % 360
            azims.append(azim_deg)
            elevs.append(90 - elev_deg)

            if orb.event and orb.event.info.startswith("LOS"):
                break

        fig_polar = Figure()
        ax_polar = fig_polar.add_subplot(111, projection="polar")
        ax_polar.set_theta_direction(-1)
        ax_polar.set_theta_zero_location("N")
        ax_polar.plot(np.radians(azims), elevs, ".")
        ax_polar.set_yticks(range(0, 90, 20))
        ax_polar.set_yticklabels(map(str, range(90, 0, -20)))
        ax_polar.set_rmax(90)
        fig_polar.tight_layout()

        buf_polar = BytesIO()
        fig_polar.savefig(buf_polar, format="png")
        buf_polar.seek(0)
        polar_data = base64.b64encode(buf_polar.getbuffer()).decode("ascii")

        # -----------------------------
        # Return both images in HTML
        # -----------------------------

        html_response = [
            f"<img src='data:image/png;base64,{map_data}'/>",
            f"<img src='data:image/png;base64,{polar_data}'/>",
            '<br>'.join(tle_visual.split("\n")),
        ]
        print([a[0:20] for a in html_response])
        return jsonify(html_response)


@app.route("/stations/<id>/dashboard/reception", methods=["GET", "POST"])
@login_required
def reception(id):
    station_address = get_station_address_by_station_id(id)
    return redirect(f"{station_address}/start_conn?frequency=103000000")


@app.route("/stations/<id>/dashboard/archive", methods=["GET", "POST"])
@login_required
def archive(id):
    return render_template("archive.html", id=id)


@app.route("/stations/<id>/dashboard/settings", methods=["GET", "POST"])
@login_required
def settings(id):
    n_status = [None, None]
    if request.method == "GET":
        info = get_station_brief_info_by_id(id)
        n_status = get_station_notif(id)

    if request.method == "POST":
        info = request.json
        mail = info["notify_mail"]
        tg = info["notify_tg"]
        time = info["early_time"]
        key = info["api_key"]
        update_station_info(id, notify_mail=mail, notify_tg=tg, early_time=time)
        if key != "":
            update_api_key(current_user.id, key)
    if n_status[0] is None:
        n_status[0] = False
    if n_status[1] is None:
        n_status[1] = False
    print(n_status)
    return render_template(
        "settings.html", info=info, notify_mail=n_status[0], notify_tg=n_status[1]
    )


@app.route("/stations/<id>/register_sdr", methods=["GET", "POST"])
@login_required
def register_sdr(id):
    if request.method == "GET":
        sdr = request.args.get("address")
        key = request.args.get("key")
        print(sdr)
        if sdr and check_api_key(key, id):
            register_sdr_bd(id, sdr)
            return {"Status": "Ok"}
        else:
            return {"Status": "Fail"}


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
