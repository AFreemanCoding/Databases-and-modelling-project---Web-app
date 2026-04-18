

# INF115 Assignment 2 – Bysykkel Shiny App
# Database lages med: python creating_db.py

import sqlite3
import pandas as pd
from shiny import App, ui, render, reactive

# Peker på databasefilen
DB_PATH = "bysykkel.db"


# Hjelpefunksjoner for å snakke med databasen --------------------------------------------------------------------------

# Brukes når vi vil hente data (SELECT)
def query_db(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df

# Brukes når vi vil endre data (INSERT, UPDATE)
def execute_db(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(sql, params)
    conn.commit()
    conn.close()


# CSS Styling – kun for utseende, ikke oppgavelogikk ---------------------------------------------------------

styling = ui.tags.style("""

    body {
        background-color: #f0f7f0;
        font-family: 'Segoe UI', sans-serif;
        color: black;
    }

    .container-fluid {
        max-width: 1400px;
        margin: 0 auto;
        padding: 30px 20px;
    }

    .app-header {
        text-align: center;
        padding: 30px 0 20px 0;
        border-bottom: 2px solid lightgreen;
        margin-bottom: 30px;
    }
    .app-header h1 { font-size: 2em; color: green; margin: 0; }
    .app-header p  { color: gray; font-size: 1em; margin-top: 6px; }

    .nav-tabs {
        border-bottom: 2px solid lightgreen;
        margin-bottom: 25px;
        display: flex;
        justify-content: center;
    }
    .nav-tabs .nav-link { color: green; font-weight: 500; border: none; padding: 10px 18px; }
    .nav-tabs .nav-link:hover { background-color: #e8f5e9; border-radius: 6px 6px 0 0; }
    .nav-tabs .nav-link.active { background-color: green !important; color: white !important; border-radius: 6px 6px 0 0; }

    h3 { color: green; font-size: 1.1em; margin-bottom: 8px; }

    table {
        width: auto;
        border-collapse: collapse;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
                        
    th { background-color: green; color: white; padding: 10px 14px; text-align: left; font-weight: 600; }
    td { padding: 9px 14px; border-bottom: 1px solid lightgray; }
    tr:last-child td { border-bottom: none; }

    .card {
        background: white;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }

    input[type="text"], select {
        border: 1px solid lightgreen;
        border-radius: 6px;
        padding: 7px 10px;
        width: 100%;
        max-width: 320px;
        margin-bottom: 10px;
    }

    .btn {
        background-color: green !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 22px !important;
        font-size: 0.95em !important;
        width: auto !important;
        min-width: 150px !important;
        cursor: pointer;
    }

    hr { border: none; border-top: 1px solid lightgray; margin: 24px 0; }

""")


# User Interface (UI) --------------------------------------------------------------

app_ui = ui.page_fluid(

    styling,
    ui.div(
        ui.tags.h1("Bysykkel 🚲"),
        ui.tags.p("Fører til god helse og hjelper miljøet."),
        class_="app-header"
    ),

    ui.navset_tab(

        # TASK 1 – Vise tabeller
        ui.nav_panel("Tabeller",
            ui.layout_columns(
                ui.div(
                    ui.h3("🚲 Sykler"),
                    ui.p("Navn, ID og status, sortert alfabetisk."),
                    ui.output_table("table_bikes"),
                    class_="card"
                ),
                ui.div(
                    ui.h3("📍 Stasjoner"),
                    ui.p("Navn, ID, plasser og prosent ledig."),
                    ui.output_table("table_stations"),
                    class_="card"
                ),
                ui.div(
                    ui.h3("🎫 Abonnementer"),
                    ui.p("Antall kjøpt per type."),
                    ui.output_table("table_subscriptions"),
                    class_="card"
                ),
                col_widths=[3, 6, 3]
            ),
        ),

        # TASK 2 – Legge til sykkel
        ui.nav_panel("Legg til sykkel",
            ui.div(
                ui.h3("Legg til ny sykkel"),
                ui.p("Navnet må kun bestå av bokstaver."),
                ui.input_text("bike_name", "Navn på ny sykkel:"),
                ui.input_action_button("add_bike", "Legg til sykkel"),
                ui.output_text("add_bike_message"),
                class_="card"
            ),
        ),

        # TASK 3 – Filtrering
        ui.nav_panel("Filtrer",
            ui.div(
                ui.h3("Filtrer sykler på status"),
                ui.input_select(
                    "filter_status",
                    "Vis sykler med status:",
                    choices=["Alle", "Active", "Parked", "Missing", "Service"],
                ),
                ui.output_table("table_bikes_filtered"),
                class_="card"
            ),
            ui.div(
                ui.h3("Stasjoner med tilgjengelige sykler"),
                ui.input_text("filter_station", "Filtrer på stasjonsnavn:"),
                ui.output_table("table_station_bikes"),
                class_="card"
            ),
        ),

        # TASK 4a – Hente sykkel
        ui.nav_panel("PICK UP",
            ui.div(
                ui.h3("Hent sykkel"),
                ui.p("Velg en parkert sykkel og trykk 'Pick up'."),
                ui.output_ui("pickup_select"),
                ui.input_action_button("pickup_btn", "Pick up"),
                ui.output_text("pickup_message"),
                class_="card"
            ),
        ),

        # TASK 4c – Servicere sykkel
        ui.nav_panel("SERVICE",
            ui.div(
                ui.h3("Servicer sykkel"),
                ui.p("Velg en sykkel, se klager, velg stasjon og trykk 'Service'."),
                ui.output_ui("service_select"),
                ui.output_table("table_complaints"),
                ui.output_ui("station_select"),
                ui.input_action_button("service_btn", "Service"),
                ui.output_text("service_message"),
                class_="card"
            ),
        ),

        # TASK 5 – Kart
        ui.nav_panel("Kart",
            ui.div(
                ui.h3("Turer per stasjon"),
                ui.p("Antall turer startet og avsluttet på hver stasjon, med lenke til OpenStreetMap."),
                ui.output_table("table_map"),
                class_="card"
            ),
        ),
    )
)


# SERVER – logikken bak appen -------------------------------------------------

def server(input, output, session):

    # refresh brukes til å oppdatere tabeller når databasen endres
    # når refresh.set() kalles, oppdateres alle tabeller som kaller refresh()
    refresh = reactive.Value(0)

    # TASK 1a – henter alle sykler sortert alfabetisk
    @output
    @render.table
    def table_bikes():
        refresh()
        return query_db("""
            SELECT bike_name AS Navn, bike_id AS ID, bike_status AS Status
            FROM Bike
            ORDER BY bike_name ASC
        """)

    # TASK 1b – henter alle stasjoner med prosent ledige plasser
    @output
    @render.table
    def table_stations():
        refresh()
        return query_db("""
            SELECT
                station_name    AS Navn,
                station_id      AS ID,
                max_spots       AS "Maks plasser",
                available_spots AS "Ledige plasser",
                ROUND(CAST(available_spots AS REAL) / max_spots * 100, 1) AS "Ledig (%)"
            FROM Station
            ORDER BY station_name ASC
        """)

    # TASK 1c – teller antall abonnementer per type (løsning på oblig 1, spørsmål 4.3)
    @output
    @render.table
    def table_subscriptions():
        return query_db("""
            SELECT subscription_type AS "Type", COUNT(*) AS "Antall kjøpt"
            FROM Subscription
            GROUP BY subscription_type
            ORDER BY COUNT(*) DESC
        """)

    # Task 2b – input_text og input_action_button i UI lager tekstfeltet og knappen.
    # Task 2c – isalpha() sjekker at navnet kun inneholder bokstaver.
    #           Gyldig navn settes inn i databasen med status Service.
    #           Ugyldig navn gir en feilmelding til brukeren.
    @output
    @render.text
    @reactive.event(input.add_bike)  # kjører kun når knappen trykkes
    def add_bike_message():
        navn = input.bike_name().strip()

        if not navn:
            return ""

        if navn.isalpha():
            # Gyldig navn – sett inn i databasen med status Service
            execute_db(
                "INSERT INTO Bike (bike_name, bike_status) VALUES (?, ?)",
                (navn, "Service")
            )
            refresh.set(refresh() + 1)
            return f"Gyldig! Sykkel '{navn}' er lagt til med status Service."
        else:
            return "Ugyldig! Navnet kan bare inneholde bokstaver."

    # TASK 3b – viser sykler filtrert på valgt status
    @output
    @render.table
    def table_bikes_filtered():
        refresh()
        status = input.filter_status()

        if status == "Alle":
            return query_db("""
                SELECT bike_name AS Navn, bike_id AS ID, bike_status AS Status
                FROM Bike ORDER BY bike_name ASC
            """)
        else:
            return query_db("""
                SELECT bike_name AS Navn, bike_id AS ID, bike_status AS Status
                FROM Bike WHERE bike_status = ?
                ORDER BY bike_name ASC
            """, params=(status,))

    # TASK 3c – viser stasjoner med parkerte sykler, kan filtreres på stasjonsnavn
    @output
    @render.table
    def table_station_bikes():
        refresh()
        filter_text = f"%{input.filter_station()}%" 
        return query_db("""
            SELECT s.station_name AS Stasjon, b.bike_name AS Sykkel, b.bike_status AS Status
            FROM Station s
            LEFT JOIN Bike b ON b.station_id = s.station_id AND b.bike_status = 'Parked'
            WHERE s.station_name LIKE ?
            ORDER BY s.station_name, b.bike_name
        """, params=(filter_text,))

    # TASK 4a – viser dropdown med bare parkerte sykler
    @output
    @render.ui
    def pickup_select():
        refresh()
        df = query_db("SELECT bike_id, bike_name FROM Bike WHERE bike_status = 'Parked' ORDER BY bike_name")
        choices = {str(row.bike_id): row.bike_name for row in df.itertuples()}
        if not choices:
            return ui.p("Ingen parkerte sykler tilgjengelig.")
        return ui.input_select("pickup_bike_id", "Velg sykkel:", choices=choices)

    # Henter valgt sykkel og oppdaterer databasen
    @output
    @render.text
    @reactive.event(input.pickup_btn)
    def pickup_message():
        df = query_db("SELECT bike_id FROM Bike WHERE bike_status = 'Parked'")
        if df.empty:
            return "Ingen parkerte sykler."

        bike_id = int(input.pickup_bike_id())

        # Hent info om sykkelen
        bike_df    = query_db("SELECT station_id, bike_name FROM Bike WHERE bike_id = ?", params=(bike_id,))
        station_id = bike_df.iloc[0]["station_id"]
        bike_name  = bike_df.iloc[0]["bike_name"]

        # Sett sykkel til Service og frigjør plassen på stasjonen
        execute_db("UPDATE Bike SET bike_status = 'Service', station_id = NULL WHERE bike_id = ?", (bike_id,))
        execute_db("UPDATE Station SET available_spots = available_spots + 1 WHERE station_id = ?", (station_id,))

        refresh.set(refresh() + 1)
        return f"Sykkel '{bike_name}' er hentet. Status satt til Service."
    
    # TASK 4b – klager er lagt til direkte i creating_db.py med INSERT INTO Complaint

    # TASK 4c – viser dropdown med bare sykler til service
    @output
    @render.ui
    def service_select():
        refresh()
        df = query_db("SELECT bike_id, bike_name FROM Bike WHERE bike_status = 'Service' ORDER BY bike_name")
        choices = {str(row.bike_id): row.bike_name for row in df.itertuples()}
        if not choices:
            return ui.p("Ingen sykler til service.")
        return ui.input_select("service_bike_id", "Velg sykkel:", choices=choices)

    # Viser klager på valgt sykkel
    @output
    @render.table
    def table_complaints():
        refresh()
        df = query_db("SELECT bike_id FROM Bike WHERE bike_status = 'Service'")
        if df.empty:
            return pd.DataFrame()
        try:
            bike_id = int(input.service_bike_id())
        except:
            return pd.DataFrame()
        return query_db("""
            SELECT complaint_type AS "Klagetype", description AS "Beskrivelse",
                   CASE resolved WHEN 0 THEN 'Ikke løst' ELSE 'Løst' END AS "Status"
            FROM Complaint WHERE bike_id = ?
        """, params=(bike_id,))

    # Viser dropdown med alle stasjoner å returnere til
    @output
    @render.ui
    def station_select():
        df = query_db("SELECT station_id, station_name FROM Station ORDER BY station_name")
        choices = {str(row.station_id): row.station_name for row in df.itertuples()}
        return ui.input_select("return_station_id", "Returner til stasjon:", choices=choices)

    # Sykkel har vært på service og returnerer den valgte stasjonen
    @output
    @render.text
    @reactive.event(input.service_btn)
    def service_message():
        df = query_db("SELECT bike_id FROM Bike WHERE bike_status = 'Service'")
        if df.empty:
            return "Ingen sykler til service."

        bike_id    = int(input.service_bike_id())
        station_id = int(input.return_station_id())
        bike_name  = query_db("SELECT bike_name FROM Bike WHERE bike_id = ?", params=(bike_id,)).iloc[0]["bike_name"]

        # Marker alle klager som løst
        execute_db("UPDATE Complaint SET resolved = 1 WHERE bike_id = ?", (bike_id,))

        # Sett sykkel til Parked og plasser den på valgt stasjon
        execute_db("UPDATE Bike SET bike_status = 'Parked', station_id = ? WHERE bike_id = ?", (station_id, bike_id))

        # Oppdater ledige plasser på stasjonen
        execute_db("UPDATE Station SET available_spots = available_spots - 1 WHERE station_id = ?", (station_id,))

        refresh.set(refresh() + 1)
        return f"Sykkel '{bike_name}' har vært på service og er nå returnert til stasjonen."

    # TASK 5 – viser turer per stasjon med lenke til OpenStreetMap
    @output
    @render.table(render_links=True, escape=False)
    def table_map():
        # Henter turer per stasjon med koordinater
        df = query_db("""
            SELECT
                s.station_name  AS Stasjon,
                s.latitude      AS lat,
                s.longitude     AS lon,
                COALESCE(starts.antall, 0) AS "Turer startet",
                COALESCE(ends.antall,   0) AS "Turer avsluttet"
            FROM Station s
            LEFT JOIN (
                SELECT start_station_id AS sid, COUNT(*) AS antall
                FROM Trip GROUP BY start_station_id
            ) starts ON starts.sid = s.station_id
            LEFT JOIN (
                SELECT end_station_id AS sid, COUNT(*) AS antall
                FROM Trip GROUP BY end_station_id
            ) ends ON ends.sid = s.station_id
            ORDER BY s.station_name
        """)

        # Lager lenke til OpenStreetMap for hver stasjon
        df["Kart"] = df.apply(
            lambda row: f'<a href="https://www.openstreetmap.org/#map=17/{row.lat}/{row.lon}">Kart</a>',
            axis=1
        )

        # Fjerner lat og lon siden de ikke skal vises i tabellen
        df = df.drop(columns=["lat", "lon"])

        return df


# Kobler UI og server sammen -------------------------------------------------

app = App(app_ui, server)