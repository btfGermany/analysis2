# BTF Media Schreibtisch-Analyse

## Übersicht
Dieses Projekt ist ein moderner, sicherer Flask-Server zur Analyse und Verwaltung von Schreibtisch-Daten (CSV + Screenshots) mit responsivem Frontend nach BTF Media Design System Guide.

## Features
- Upload von Analyse-Ordnern (CSV + Screenshots)
- Automatische Schreibtisch-Erstellung mit UUID-Link
- Passwortschutz (optional, sicher gehasht)
- CRUD & Filter für CSV-Daten, Screenshot-Galerie
- Moderne Visualisierung (Tabellen, Graphen, Galerie)
- SQLite3-Datenbank, Tailwind CSS, Glasmorphismus, Dark/Light-Mode

## Installation
1. **Python 3.9+ installieren**
2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Tailwind CSS bauen:**
   ```bash
   npm install
   npx tailwindcss -i ./static/src/input.css -o ./static/dist/output.css --watch
   ```
4. **Server starten:**
   ```bash
   flask run
   ```

## Nutzung
1. Weboberfläche öffnen (`http://localhost:5000`)
2. Analyse-Ordner (ZIP) hochladen
3. Schreibtisch-Link & (optional) Passwort erhalten
4. Daten durchsuchen, filtern, bearbeiten, Screenshots ansehen
5. Schreibtisch-Link + Passwort speichern für späteren Zugriff

## Hinweise
- CSV kann beliebige Spalten enthalten (werden dynamisch erkannt)
- Passwörter werden sicher gehasht (bcrypt)
- Schreibtisch-Links sind nicht erratbar (UUIDv4)
- Daten werden in `/workspaces/<uuid>/` gespeichert, Pfade in DB

## Design
- Minimalistisch, Glasmorphismus, sanfte Animationen
- Dark/Light-Mode, Theme-Toggle
- Responsiv, barrierearm, moderne UX

## Lizenz
MIT