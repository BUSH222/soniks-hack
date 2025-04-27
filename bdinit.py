from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbmanager import Base,User,Station,Ownership
engine = create_engine("postgresql://postgres:postgres@localhost/soniks")

def init_bd():
    Base.metadata.create_all(bind=engine)

def populate_base_data():
    db_session = sessionmaker(bind=engine)
    bob = User(name = "Bob",password = '123')
    bob_station = Station(name='NIGGER',lat=55.7522,long=37.6156,alt=123)
    bob_own = Ownership(user_id=1,station_id=1)
    db_session.add_all([bob,bob_own,bob_station])
    try:
        db_session.commit()
    except Exception as e:
        raise e
  
