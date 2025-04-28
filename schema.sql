create table if not exists "user"(
    id serial primary key,
    name VARCHAR(32) NOT NULL,
    password VARCHAR(32) UNIQUE NOT NULL,
    tg VARCHAR(32),
    api_key VARCHAR(32) UNIQUE,
    email VARCHAR(32)
);

create table if not exists station(
    id serial primary key,
    name VARCHAR(32) NOT NULL,
    lat FLOAT NOT NULL,
    long FLOAT NOT NULL,
    alt INT NOT NULL,
    notify_mail Boolean,
    notify_tg Boolean,
    early_time TIME,
    sdr_server_address VARCHAR(32)
);

create table if not exists ownership(
    id serial primary key,
    user_id INT REFERENCES "user"(id),
    station_id INT REFERENCES station(id)
);
