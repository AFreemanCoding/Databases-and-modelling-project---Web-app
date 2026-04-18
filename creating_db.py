import sqlite3
import csv 

conn = sqlite3.connect("bysykkel.db")
cur = conn.cursor()


cur.execute(""" 
    CREATE TABLE User (
        user_id      INTEGER PRIMARY KEY,
        user_name    TEXT    NOT NULL, 
        phone_number INTEGER     
    )
""")


cur.execute("""
    CREATE TABLE Station (
        station_id      INTEGER PRIMARY KEY, 
        station_name    TEXT    NOT NULL,
        latitude        REAL,
        longitude       REAL,
        max_spots       INTEGER,
        available_spots INTEGER          
    )            
""")

# Task 2a – CHECK-constraint sørger for at bike_status kun kan være en av fire verdier.
# Hvis man prøver å sette en annen verdi, vil SQLite avvise det med en feil.
cur.execute("""
    CREATE TABLE Bike (
        bike_id         INTEGER PRIMARY KEY,
        bike_name       TEXT    NOT NULL,
        bike_status     TEXT    NOT NULL DEFAULT 'Service'
                        CHECK(bike_status IN ('Active', 'Parked', 'Missing', 'Service')),
        station_id      INTEGER REFERENCES Station(station_id)
    )
""")


cur.execute("""
    CREATE TABLE Subscription (
        subscription_id     INTEGER PRIMARY KEY,
        subscription_type   TEXT    NOT NULL, 
        start_time          TEXT,
        user_id             INTEGER REFERENCES User(user_id)
    )
""")


cur.execute("""
    CREATE TABLE Trip (
        trip_id             INTEGER PRIMARY KEY,
        trip_start_time     TEXT,
        trip_end_time       TEXT,
        start_station_id    INTEGER REFERENCES Station(station_id),
        end_station_id      INTEGER REFERENCES Station(station_id),
        bike_id             INTEGER REFERENCES Bike(bike_id),
        user_id             INTEGER REFERENCES User(user_id)
    )
""")


cur.execute("""
    CREATE TABLE Complaint (
        complaint_id        INTEGER PRIMARY KEY,
        bike_id             INTEGER REFERENCES Bike(bike_id), 
        complaint_type      TEXT    NOT NUll, 
        description         TEXT,
        resolved            INTEGER     NOT NULL    DEFAULT '0'
    )
""")

# set() brukes for å holde styr på hvilke IDer som allerede er satt inn.
# Dette hindrer duplikater siden samme bruker/stasjon kan dukke opp på flere rader i CSV-filen.
seen_users = set()
seen_stations = set()
seen_bikes = set()
seen_subscriptions = set()
seen_trips = set()


with open("bysykkel.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        
        # For User
        if row['user_id'] and row['user_id'] not in seen_users:
            cur.execute("INSERT INTO User VALUES (?, ?, ?)",
                (row['user_id'], row['user_name'], row['user_phone_number']))
            seen_users.add(row['user_id'])

        # For Station
        if row['start_station_id'] and row['start_station_id'] not in seen_stations:
            cur.execute("INSERT INTO Station VALUES (?, ?, ?, ?, ?, ?)",
                (row['start_station_id'], row['start_station_name'],
                 row['start_station_latitude'], row['start_station_longitude'],
                 row['start_station_max_spots'], row['start_station_available_spots']))
            seen_stations.add(row['start_station_id'])

        # For bike
        if row['bike_id'] and row['bike_id'] not in seen_bikes:
            cur.execute("INSERT INTO Bike VALUES (?, ?, ?, ?)",
                (row['bike_id'], row['bike_name'],
                 row['bike_status'], row['bike_station_id']))
            seen_bikes.add(row['bike_id'])

        # For subscription
        if row['subscription_id'] and row['subscription_id'] not in seen_subscriptions:
            cur.execute("INSERT INTO Subscription VALUES (?, ?, ?, ?)",
                (row['subscription_id'], row['subscription_type'],
                 row['subscription_start_time'], row['user_id']))
            seen_subscriptions.add(row['subscription_id'])

        # For trip 
        if row['trip_id'] and row['trip_id'] not in seen_trips:
            cur.execute("INSERT INTO Trip VALUES (?, ?, ?, ?, ?, ?, ?)",
                (row['trip_id'], row['trip_start_time'], row['trip_end_time'],
                 row['start_station_id'], row['end_station_id'],
                 row['bike_id'], row['user_id']))
            seen_trips.add(row['trip_id'])

# Legger til klager manuelt 
cur.execute("INSERT INTO Complaint (bike_id, complaint_type, description) VALUES (3, 'Flat tire', 'Front wheel flat')")
cur.execute("INSERT INTO Complaint (bike_id, complaint_type, description) VALUES (6, 'Broken light', 'Front light missing')")
cur.execute("INSERT INTO Complaint (bike_id, complaint_type, description) VALUES (7, 'Loose handlebar', 'Handlebar wobbles')")


conn.commit()
conn.close()

