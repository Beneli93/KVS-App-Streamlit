# KVS-App – Kunden- und Terminverwaltung

Dieses Projekt ist ein **Prototyp für das Management von Kundendaten**.  
Ziel ist ein flexibles System zur **Speicherung, Bearbeitung und Anzeige von Kundendaten** inklusive Terminen.

## Kundendaten

### Pflichtfelder pro Kunde
- Anrede (Herr, Frau, Divers)
- Vorname
- Nachname
- Geschlecht
- Alter
- E-Mail-Adresse
- PLZ
- Wohnort(e)
- Telefon
- Mobil
- **Eindeutige ID** (wird automatisch generiert)

### Optionale Felder
- Termine: Datum, Uhrzeit und Notiz
- Weitere individuelle Informationen (kann leicht erweitert werden)

## Funktionen der App

- **Kundenverwaltung**  
  - Kunde anlegen, bearbeiten und löschen  
  - Suche nach Vorname, Nachname, ID, PLZ, Wohnort, Telefon, Mobil oder E-Mail  

- **Terminverwaltung**  
  - Termine pro Kunde anlegen, bearbeiten, löschen  
  - Anzeige kommender Termine (7 Tage Vorschau)  
  - Nächster Termin wird hervorgehoben  

- **Persistente Speicherung**  
  - Kundendaten und Termine werden in einer **JSON-Datei** gespeichert  
  - Daten bleiben nach Beenden der App erhalten

## Technologie

- **Python 3.13+**  
- **Streamlit** – für die GUI  
- **Pandas** – für Tabellen und Datenbearbeitung  
- **JSON** – für die persistente Speicherung

## Nutzung

1. Repository klonen oder Dateien direkt auf GitHub nutzen  
2. Benötigte Pakete installieren:
   ```bash
   pip install -r requirements.txt
