"""
setup_db.py
-----------
Oppretter en normalisert bysykkel.db SQLite-database fra rådata.

Tabellstruktur (normalisert fra oblig 1):
  - User           : brukere
  - Subscription   : abonnementer (kobles til User)
  - Station        : sykkelstasjoner
  - Bike           : sykler (kobles til Station)
  - Trip           : turer (kobles til User, Bike, Station x2)
  - Complaint      : klager på sykler (legges til i Task 4)
"""

import sqlite3
import os

DB_PATH = "bysykkel.db"

# Slett gammel db hvis den finnes, slik at vi starter helt friskt
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ── 1. OPPRETT TABELLER ─────────────────────────────────────────────────────

# User-tabell
cur.execute("""
CREATE TABLE User (
    user_id      INTEGER PRIMARY KEY,
    user_name    TEXT    NOT NULL,
    phone_number INTEGER
)
""")

# Station-tabell
cur.execute("""
CREATE TABLE Station (
    station_id        INTEGER PRIMARY KEY,
    station_name      TEXT    NOT NULL,
    latitude          REAL,
    longitude         REAL,
    max_spots         INTEGER,
    available_spots   INTEGER
)
""")

# Bike-tabell
# Vi bruker CHECK for å begrense bike_status til gyldige verdier (Task 2a)
cur.execute("""
CREATE TABLE Bike (
    bike_id    INTEGER PRIMARY KEY,
    bike_name  TEXT    NOT NULL,
    bike_status TEXT   NOT NULL DEFAULT 'Service'
                       CHECK(bike_status IN ('Active', 'Parked', 'Missing', 'Service')),
    station_id INTEGER REFERENCES Station(station_id)
)
""")

# Subscription-tabell
cur.execute("""
CREATE TABLE Subscription (
    subscription_id   INTEGER PRIMARY KEY,
    subscription_type TEXT    NOT NULL,
    start_time        TEXT,
    user_id           INTEGER REFERENCES User(user_id)
)
""")

# Trip-tabell
cur.execute("""
CREATE TABLE Trip (
    trip_id          INTEGER PRIMARY KEY,
    trip_start_time  TEXT,
    trip_end_time    TEXT,
    start_station_id INTEGER REFERENCES Station(station_id),
    end_station_id   INTEGER REFERENCES Station(station_id),
    bike_id          INTEGER REFERENCES Bike(bike_id),
    user_id          INTEGER REFERENCES User(user_id)
)
""")

# Complaint-tabell (brukes i Task 4)
cur.execute("""
CREATE TABLE Complaint (
    complaint_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    bike_id        INTEGER REFERENCES Bike(bike_id),
    complaint_type TEXT    NOT NULL,
    description    TEXT,
    resolved       INTEGER NOT NULL DEFAULT 0  -- 0 = ikke løst, 1 = løst
)
""")

# ── 2. FYLL INN DATA ────────────────────────────────────────────────────────

# Brukere
users = [
    (1,  'Ole Olesen',          12345678),
    (2,  'Vilde Sørensen',      54140106),
    (3,  'Stig Wilhelmsen',     94390764),
    (4,  'Markus Karlsen',      32507021),
    (5,  'Kristine Halseth',    32641181),
    (6,  'Anders Hansen',       57527858),
    (7,  'Per Arnesen',         11223344),
    (8,  'Kjersti Pham',        26720981),
    (9,  'Erling Ruud',         83997261),
    (10, 'Kine Pedersen',       33866539),
    (11, 'Rune Vang',           42135422),
    (12, 'Madeleine Sørensen',  21968827),
    (14, 'Roger Lie',           79595257),
    (15, 'Vibeke Indrebø',      37715005),
    (16, 'Thomas Olsen',        76929790),
    (17, 'Kari Hansen',          1884971),
    (18, 'Mari Siljesen',       22115577),
    (19, 'Anders Jakobsen',     63507721),
    (20, 'Tor Antonsen',        63570173),
]
cur.executemany("INSERT INTO User VALUES (?,?,?)", users)

# Stasjoner
stations = [
    (1, 'Høyteknologisenteret', 60.382216, 5.332288, 66, 34),
    (2, 'Nygårdsporten',        60.383964, 5.333448, 27,  8),
    (3, 'Festplassen',          60.391270, 5.325756, 24, 23),
    (4, 'Småstrandgaten',       60.393001, 5.326816, 24, 16),
    (5, 'Torgallmenningen',     60.392954, 5.323628, 22,  4),
]
cur.executemany("INSERT INTO Station VALUES (?,?,?,?,?,?)", stations)

# Sykler (bike_station_id=4 for Missing/Active sykler – de er ikke parkert, men knyttet til siste stasjon)
bikes = [
    (1,  'Morten',  'Missing', 4),
    (2,  'Sara',    'Active',  2),
    (3,  'Ida',     'Parked',  2),
    (4,  'Hege',    'Active',  3),
    (5,  'Henrik',  'Parked',  5),
    (6,  'Trine',   'Parked',  2),
    (7,  'Frank',   'Parked',  4),
    (8,  'Thea',    'Parked',  1),
    (9,  'Roar',    'Parked',  1),
    (10, 'Preben',  'Missing', 4),
    (11, 'Marie',   'Parked',  3),
    (12, 'Annette', 'Parked',  5),
    (13, 'Elin',    'Missing', 2),
    (14, 'Andreas', 'Active',  2),
    (15, 'Runar',   'Active',  5),
]
cur.executemany("INSERT INTO Bike VALUES (?,?,?,?)", bikes)

# Abonnementer
subscriptions = [
    (1,  'Week',  '2019-07-30 17:00:19', 2),
    (2,  'Week',  '2020-05-12 22:38:24', 4),
    (4,  'Year',  '2018-01-20 04:59:03', 2),
    (7,  'Day',   '2018-06-07 02:08:39', 5),
    (16, 'Month', '2020-06-14 12:45:57', 3),
    (19, 'Month', '2019-03-25 09:14:10', 4),
    (24, 'Year',  '2018-08-30 10:40:59', 3),
    (28, 'Month', '2021-01-18 19:30:07', 5),
    (31, 'Week',  '2019-12-19 22:32:45', 3),
    (32, 'Week',  '2018-10-13 14:48:46', 5),
]
cur.executemany("INSERT INTO Subscription VALUES (?,?,?,?)", subscriptions)

# Turer
trips = [
    (1, '2019-08-04 13:12:10', '2019-08-04 13:21:04', 4, 2,  6,  2),
    (2, '2021-02-10 08:53:14', '2021-02-10 09:07:32', 2, 1,  8,  9),
    (3, '2021-01-27 16:01:08', '2021-01-27 16:42:11', 5, 1,  9, 11),
    (4, '2021-02-13 19:18:42', '2021-02-13 19:24:02', 3, 5, 12, 16),
    (5, '2021-02-01 09:30:08', '2021-02-01 09:32:04', 1, 3, 11,  5),
    (6, '2021-03-02 10:36:09', '2021-03-02 12:29:09', 1, 2,  3,  7),
]
cur.executemany("INSERT INTO Trip VALUES (?,?,?,?,?,?,?)", trips)

# Klager (for Task 4b – minst 3 sykler med status Parked)
# Sykler med Parked: 3(Ida), 5(Henrik), 6(Trine), 7(Frank), 8(Thea), 9(Roar), 11(Marie), 12(Annette)
complaints = [
    (3,  'Flat tire',        'Front wheel flat'),
    (3,  'Broken brake',     'Left brake does not work'),
    (6,  'Broken light',     'Front light missing'),
    (7,  'Loose handlebar',  'Handlebar wobbles'),
    (7,  'Gear problem',     'Cannot shift to gear 3'),
    (11, 'Rusty chain',      'Chain makes noise'),
]
cur.executemany(
    "INSERT INTO Complaint(bike_id, complaint_type, description) VALUES (?,?,?)",
    complaints
)

conn.commit()
conn.close()
print("✅ bysykkel.db opprettet og fylt med data!")

# Verifiser
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
for table in ['User', 'Station', 'Bike', 'Subscription', 'Trip', 'Complaint']:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table}: {cur.fetchone()[0]} rader")
conn.close()