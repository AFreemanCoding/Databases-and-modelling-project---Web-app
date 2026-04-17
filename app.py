# app.py
# INF115 Oblig 2 – Bysykkel Shiny App
# Kjør med: python -m shiny run --reload app.py

import sqlite3
import pandas as pd
from shiny import App, ui, render, reactive

DB_PATH = "bysykkel_1.db"

def query_db(sql: str, params=()) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df

def execute_db(sql: str, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(sql, params)
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════════════════════
#  ESTETIKK – alt i denne seksjonen er kun for utseende, ikke oppgavelogikk
# ════════════════════════════════════════════════════════════════════════════

styling = ui.tags.style("""

    /* Generell side */
    body {
        background-color: #f0f7f0;
        font-family: 'Segoe UI', sans-serif;
        color: #1a1a1a;
    }

    /* Sentrert innhold med maks bredde */
    .container-fluid {
        max-width: 1400px;
        margin: 0 auto;
        padding: 30px 20px;
    }

    /* Header øverst */
    .app-header {
        text-align: center;
        padding: 30px 0 20px 0;
        border-bottom: 2px solid #c8e6c9;
        margin-bottom: 30px;
    }
    .app-header h1 {
        font-size: 2em;
        color: #2e7d32;
        margin: 0;
    }
    .app-header p {
        color: #555;
        font-size: 1em;
        margin-top: 6px;
    }

    /* Faner – sentrert */
    .nav-tabs {
        border-bottom: 2px solid #a5d6a7;
        margin-bottom: 25px;
        display: flex;
        justify-content: center;
    }
    .nav-tabs .nav-link {
        color: #2e7d32;
        font-weight: 500;
        border: none;
        padding: 10px 18px;
    }
    .nav-tabs .nav-link:hover {
        background-color: #e8f5e9;
        border-radius: 6px 6px 0 0;
    }
    .nav-tabs .nav-link.active {
        background-color: #4caf50 !important;
        color: white !important;
        border-radius: 6px 6px 0 0;
    }

    /* Seksjonsoverskrifter */
    h3 {
        color: #2e7d32;
        font-size: 1.1em;
        margin-bottom: 8px;
    }

    /* Tabeller */
    table {
        width: auto;
        border-collapse: collapse;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    th {
        background-color: #43a047;
        color: white;
        padding: 10px 14px;
        text-align: left;
        font-weight: 600;
    }
    td {
        padding: 9px 14px;
        border-bottom: 1px solid #f1f1f1;
    }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background-color: #f9fbe7; }

    /* Kort-boks rundt hver oppgave */
    .card {
        background: white;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }

    /* Input-felter */
    input[type="text"], select {
        border: 1px solid #a5d6a7;
        border-radius: 6px;
        padding: 7px 10px;
        width: 100%;
        max-width: 320px;
        margin-bottom: 10px;
    }

    /* Knapper */
    .btn {
        background-color: #43a047 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 22px !important;
        font-size: 0.95em !important;
        cursor: pointer;
    }
    .btn:hover { background-color: #388e3c !important; }

    /* Skillelinje */
    hr { border: none; border-top: 1px solid #e0e0e0; margin: 24px 0; }

""")

# ════════════════════════════════════════════════════════════════════════════
#  UI
# ════════════════════════════════════════════════════════════════════════════

app_ui = ui.page_fluid(

    # ── ESTETIKK: CSS og header ───────────────────────────────────────────────
    styling,
    ui.div(
        ui.tags.h1("Bysykkel 🚲 "),
        ui.tags.p("Fører til god helse og hjelper miljøet."),
        class_="app-header"
    ),

    ui.navset_tab(

        # ── TASK 1 ───────────────────────────────────────────────────────────
        ui.nav_panel("Tabeller",

            # ESTETIKK: tre kort ved siden av hverandre på task 1
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

        # ── TASK 2 ───────────────────────────────────────────────────────────
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

        # ── TASK 3 ───────────────────────────────────────────────────────────
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

        # ── TASK 4a: PICK UP ─────────────────────────────────────────────────
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

        # ── TASK 4c: SERVICE ─────────────────────────────────────────────────
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

        # ── TASK 5 ───────────────────────────────────────────────────────────
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


# ════════════════════════════════════════════════════════════════════════════
#  SERVER  –  kun oppgavelogikk herfra
# ════════════════════════════════════════════════════════════════════════════

def server(input, output, session):

    refresh = reactive.Value(0)

    # ── Task 1a: Sykler ──────────────────────────────────────────────────────
    @output
    @render.table
    def table_bikes():
        refresh()
        return query_db("""
            SELECT bike_name AS Navn, bike_id AS ID, bike_status AS Status
            FROM Bike ORDER BY bike_name ASC
        """)

    # ── Task 1b: Stasjoner ───────────────────────────────────────────────────
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

    # ── Task 1c: Abonnementstyper ────────────────────────────────────────────
    @output
    @render.table
    def table_subscriptions():
        return query_db("""
            SELECT subscription_type AS "Type", COUNT(*) AS "Antall kjøpt"
            FROM Subscription
            GROUP BY subscription_type
            ORDER BY COUNT(*) DESC
        """)

    # ── Task 2: Legg til sykkel ──────────────────────────────────────────────
    @output
    @render.text
    @reactive.event(input.add_bike)
    def add_bike_message():
        navn = input.bike_name().strip()
        if not navn:
            return ""
        if navn.isalpha():
            execute_db("INSERT INTO Bike (bike_name, bike_status) VALUES (?, ?)", (navn, "Service"))
            refresh.set(refresh() + 1)
            return f"✅ Gyldig! Sykkel '{navn}' er lagt til med status Service."
        else:
            return "❌ Ugyldig! Navnet kan bare inneholde bokstaver."

    # ── Task 3b: Filtrer sykler ──────────────────────────────────────────────
    @output
    @render.table
    def table_bikes_filtered():
        refresh()
        status = input.filter_status()
        if status == "Alle":
            return query_db("SELECT bike_name AS Navn, bike_id AS ID, bike_status AS Status FROM Bike ORDER BY bike_name ASC")
        else:
            return query_db("SELECT bike_name AS Navn, bike_id AS ID, bike_status AS Status FROM Bike WHERE bike_status = ? ORDER BY bike_name ASC", params=(status,))

    # ── Task 3c: Stasjoner med sykler ────────────────────────────────────────
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

    # ── Task 4a: PICK UP ─────────────────────────────────────────────────────
    @output
    @render.ui
    def pickup_select():
        refresh()
        df = query_db("SELECT bike_id, bike_name FROM Bike WHERE bike_status = 'Parked' ORDER BY bike_name")
        choices = {str(row.bike_id): row.bike_name for row in df.itertuples()}
        if not choices:
            return ui.p("Ingen parkerte sykler tilgjengelig.")
        return ui.input_select("pickup_bike_id", "Velg sykkel:", choices=choices)

    @output
    @render.text
    @reactive.event(input.pickup_btn)
    def pickup_message():
        df = query_db("SELECT bike_id FROM Bike WHERE bike_status = 'Parked'")
        if df.empty:
            return "Ingen parkerte sykler."
        bike_id    = int(input.pickup_bike_id())
        bike_df    = query_db("SELECT station_id, bike_name FROM Bike WHERE bike_id = ?", params=(bike_id,))
        station_id = bike_df.iloc[0]["station_id"]
        bike_name  = bike_df.iloc[0]["bike_name"]
        execute_db("UPDATE Bike SET bike_status = 'Service', station_id = NULL WHERE bike_id = ?", (bike_id,))
        execute_db("UPDATE Station SET available_spots = available_spots + 1 WHERE station_id = ?", (station_id,))
        refresh.set(refresh() + 1)
        return f"✅ Sykkel '{bike_name}' er hentet. Status satt til Service."

    # ── Task 4c: SERVICE ─────────────────────────────────────────────────────
    @output
    @render.ui
    def service_select():
        refresh()
        df = query_db("SELECT bike_id, bike_name FROM Bike WHERE bike_status = 'Service' ORDER BY bike_name")
        choices = {str(row.bike_id): row.bike_name for row in df.itertuples()}
        if not choices:
            return ui.p("Ingen sykler til service.")
        return ui.input_select("service_bike_id", "Velg sykkel:", choices=choices)

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

    @output
    @render.ui
    def station_select():
        df = query_db("SELECT station_id, station_name FROM Station ORDER BY station_name")
        choices = {str(row.station_id): row.station_name for row in df.itertuples()}
        return ui.input_select("return_station_id", "Returner til stasjon:", choices=choices)

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
        execute_db("UPDATE Complaint SET resolved = 1 WHERE bike_id = ?", (bike_id,))
        execute_db("UPDATE Bike SET bike_status = 'Parked', station_id = ? WHERE bike_id = ?", (station_id, bike_id))
        execute_db("UPDATE Station SET available_spots = available_spots - 1 WHERE station_id = ?", (station_id,))
        refresh.set(refresh() + 1)
        return f"✅ Sykkel '{bike_name}' er servicert og returnert til stasjon."

    # ── Task 5: Kart ─────────────────────────────────────────────────────────
    @output
    @render.table(render_links=True, escape=False)
    def table_map():
        return query_db("""
            SELECT
                s.station_name AS Stasjon,
                COALESCE(starts.antall, 0) AS "Turer startet",
                COALESCE(ends.antall,   0) AS "Turer avsluttet",
                '<a href="https://www.openstreetmap.org/#map=17/'
                    || s.latitude || '/' || s.longitude
                    || '">Kart</a>' AS Kart
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


# ════════════════════════════════════════════════════════════════════════════
#  APP
# ════════════════════════════════════════════════════════════════════════════

app = App(app_ui, server)