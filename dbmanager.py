from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, declarative_base
from helper import generate_coordinate_id

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String,unique=True)
    tg = Column(String)
    api_key = Column(String)
    email = Column(String)


class Station(Base):
    __tablename__ = "station"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    lat = Column(Float)
    long = Column(Float)
    alt = Column(Float)
    notify_mail = Column(Boolean)
    notify_tg = Column(Boolean)
    early_time = Column(Integer)
    sdr_server_address = Column(String)


class Ownership(Base):
    __tablename__ = "ownership"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    station_id = Column(Integer, ForeignKey("station.id"))


engine = create_engine("postgresql://postgres:postgres@localhost/soniks")
Session = sessionmaker(bind=engine)
db_session = Session()


def update_station_info(station_id, **kwargs):
    station = db_session.query(Station).get(station_id)
    if not station:
        return None
    for field, value in kwargs.items():
        setattr(station, field, value)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
def update_api_key(user_id,api_key):
    user = db_session.query(User).filter(User.id == user_id).first()
    user.api_key = api_key
    print(user.id,api_key)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def check_api_key(key,station_id):
    user_with_api = db_session.query(User).filter(User.api_key == key).first()
    print(user_with_api.name)
    if user_with_api:
        owner = db_session.query(Ownership).filter(Ownership.station_id == station_id and Ownership.user_id == user_with_api.id)
        print(f'ASDASD {owner.first().user_id}')
        if owner.first().user_id ==user_with_api.id:
            return True
    return False

def get_station_owner(station_id):
    owner_id = db_session.query(Ownership).filter(Ownership.station_id == station_id).first()
    owner_name = db_session.query(User).filter(User.id == owner_id.user_id).first()
    return owner_name.name

def register_sdr_bd(sid,sdr):
    station = db_session.query(Station).filter(Station.id == sid).first()
    if station:
        station.sdr_server_address = sdr
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def get_station_brief_info_by_id(station_id):
    station = db_session.query(Station).filter(Station.id == station_id).first()
    location = generate_coordinate_id(station.lat, station.long)
    info = [station.id,station.name, location]
    return info


def get_stations_by_user_id(user_id):
    stations = db_session.query(Ownership).filter(Ownership.user_id == user_id).all()
    res = []
    for station in stations:
        res.append(station.station_id)
    return res

def get_user_id_by_name(name):
    user = db_session.query(User).filter(User.name == name).first()
    if user:
        return user.id
    return None

def confirm_ownership(user_id,station_id):
    t = db_session.query(Ownership).filter(Ownership.station_id == station_id).all()
    for i in t:
        if i.user_id == user_id:
            return True
    return False
def get_full_station_info_by_id(id):
    info = db_session.query(Station).filter(Station.id == id).first()
    location = generate_coordinate_id(info.lat, info.long)
    return [info.id,info.name,location,info.lat,info.long,info.alt]

def get_all_user_data_by_name(name):
    data = db_session.query(User).filter(User.name == name).first()
    if data:
        return [data.id,data.name,data.password]
    else:
        return "No such user"

def get_all_user_data_by_id(id):
    data = db_session.query(User).filter(User.id == id).first()
    if data:
        return [data.id,data.name,data.password]
    else:
        return "No such user"

def get_station_address_by_station_id(id):
    data = db_session.query(Station).filter(Station.id == id).first()
    if data:
        return data.sdr_server_address
    else:
        return "None set"
