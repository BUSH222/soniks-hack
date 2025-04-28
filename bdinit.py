from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbmanager import Base,User,Station,Ownership
engine = create_engine("postgresql://postgres:12345678@localhost/soniks")

def init_bd():
    Base.metadata.create_all(bind=engine)

def populate_base_data():
    Session = sessionmaker(bind=engine)
    db_session = Session()
    bob = User(name = "Bob",password = '123')
    bob_station = Station(name='RAAAA',lat=55.7522,long=37.6156,alt=123, sdr_server_address='http://192.168.196.51:8000')
    nana = User(name = "Nana", password = '123123')
    nana_station = Station(name='nanasss',lat=55.1123,long=32.6156,alt=11233, sdr_server_address='http://google.com')
    db_session.add_all([bob,bob_station,nana,nana_station])
    
    try:
        db_session.commit()
    except Exception as e:
        raise e
    user_id = db_session.query(User).first().id
    station_id = db_session.query(Station).all()[0].id
    bob_own = Ownership(user_id=user_id,station_id=station_id)
    nana_own = Ownership(user_id=2,station_id=2)
    db_session.add_all([bob_own,nana_own])
    try:
        db_session.commit()
    except Exception as e:
        raise e
