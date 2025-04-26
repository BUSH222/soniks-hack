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
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    tg = Column(String)
    email = Column(String)


class Station(Base):
    __tablename__ = "stations"
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
    user_id = Column(Integer, ForeignKey("users.id"))
    station_id = Column(Integer, ForeignKey("stations.id"))


engine = create_engine("postgresql://user:password@localhost/dbname")
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


def get_station_owner(station_id):
    owner_id = db_session.query(Ownership).filter(Ownership.station_id == station_id)[0]
    owner_name = db_session.query(User).filter(User.id == owner_id).first()
    return owner_name


def get_station_brief_info_by_id(station_id):
    station = db_session.query(Station).filter(Station.id == station_id)
    location = generate_coordinate_id(station.lat, station.long)
    info = [station.name, location, station.lat, station.long, station.alt]
    return info


def get_stations_by_user_id(user_id):
    stations = db_session.query(Ownership).filter(Ownership.user_id == user_id)
    return stations


def get_user_id_by_name(name):
    user = db_session.query(User).filter(User.name == name).first()
    if user:
        return user.id
    return None


def get_full_station_info_by_id(id):
    info = db_session.query(Station).filter(Station.id == id)
    return info

def get_all_user_data_by_name(name):
    data = db_session.query(User).filter(User.name == name).first()
    return data