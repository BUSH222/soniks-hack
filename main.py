from flask import Flask, redirect, render_template, request, url_for, abort, Response
from flask_login import login_required
from flask_login import login_user, LoginManager, current_user, login_required, UserMixin, logout_user
from sqlalchemy import select, func, extract, and_, inspect
from sqlalchemy.orm import Session
from dbmanager import (get_all_user_data_by_name,get_stations_by_user_id,get_user_id_by_name,get_station_brief_info_by_id,get_full_station_info_by_id,get_station_owner,update_station_info)
import urllib.parse
import requests
from datetime import datetime
from dateutil.parser import parse
from helper import generate_coordinate_id


app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email


@app.route('/')
def index():
    return render_template("login_with.html")


@app.route('/login_password', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = list(get_all_user_data_by_name(username))
        print(user_data)
        if user_data:
            if user_data[2] == password and len(password) < 32:
                user = User(*user_data)
                login_user(user)
                return redirect(url_for('user_stations'))
            else:
                return "Invalid username or password"
    return render_template('login_password.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def main():
    return('main.html')

@app.route('/users/<current_user.name>', methods=['GET', 'POST'])
@login_required
def user_stations():
    info = []
    if request.method == "GET":
        user_id = get_user_id_by_name(current_user.name)
        stations_id =get_stations_by_user_id(user_id)
        for id in stations_id:
            ex = get_station_brief_info_by_id(id)
            info.append(ex)
    return render_template("stations.html",stations = info)

@app.route('/stations/<id>', methods=['GET', 'POST'])
@login_required
def station(id):
    user_id = get_user_id_by_name(current_user.name)
    user_owned_stations = get_stations_by_user_id(user_id)
    if user_id in user_owned_stations:
        change_button = True
    if request.method == "GET":
        owner = get_station_owner(id)
        info = get_full_station_info_by_id(id)
        info.append(owner)
    return render_template("stations.html",info=info,change_button=change_button)


@app.route('/stations/<id>/dashboard', methods=['GET', 'POST'])
@login_required
def station_dashboard(id):
    return render_template("stations_map.html",id=id)



@app.route('/stations/edit/<id>', methods=['GET', 'POST'])
@login_required   
def edit_station(id):
    if request.method == "GET":
        info = get_full_station_info_by_id(id)
    if request.method == "POST":
            name = request.form["name"]
            lat = request.form["lat"]
            long = request.form["long"]
            alt = request.form["alt"]
            notif_mai = request.form["notif_mai"]
            notif_tg = request.form["notif_tg"]
            early_time = request.form["early_time"]
            sdr_server_address = request.form["sdr_server_address"]
            update_station_info(id,name = name,lat = lat,long = long,alt= alt,notif_mai= notif_mai,notif_tg= notif_tg,early_time= early_time, sdr_server_address=sdr_server_address)
            return(redirect(url_for('satation',id=id)))

    return render_template("stations_editor.html",info = info)


