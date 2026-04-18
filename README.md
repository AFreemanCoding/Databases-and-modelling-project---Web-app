# INF115 – Databaser and Modellering, Assignment 2
Dette prosjektet var gjort som en del av arbeidskravene i emnet INF115 - Databaser og modellering (ved UiB)

Denne oppgaven ba oss om å lage en web-applikasjon med bruk av Shiny for Python, og SQLlite som database (backend).
Appen styrer et bysykkel-system med stasjoner, sykler, turer blant andre ting.

## Funksjoner
- Se sykler, stasjoner og abonnementsdata
- Legg til nye sykler med navnevalidering
- Filtrer sykler på status og stasjoner på navn
- Hent og servicer sykler
- Se turstatistikk per stasjon med lenker til OpenStreetMap

## Database
Databasen opprettes ved å kjøre `creating_db.py`, som setter opp alle tabeller og importerer data fra `bysykkel.csv`.
SQL-queries brukes gjennom hele appen for å hente og oppdatere data, inkludert SELECT, INSERT, UPDATE, JOIN, GROUP BY og COUNT.

## Styling
CSS ble lagt til for å gjøre appen mer presentabel, med grønt tema som kan minne om bysykkel appen

# Hvordan man kjører appen
Først må man bruke pip install shiny (for å installere shiny, åpenbart heh)
Så kjør: python create_db.py
Til slutt kjør: python -m shiny run app.py

