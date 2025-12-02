# FHIR Medical Data Transformer

Ein **Python-basiertes Tool** zur Transformation medizinischer Rohdaten in das standardisierte **FHIR-Format** (Fast Healthcare Interoperability Resources).

Das Tool verarbeitet medizinische Textdaten und Codes (z. B. **ICD-10**, **OPS**, **LOINC**) und wandelt sie in strukturierte FHIR-Ressourcen um, um die interoperable Übertragung von Patientendaten, Diagnosen, Therapieplänen, Laborwerten und Bildgebungsinformationen zwischen verschiedenen Gesundheitssystemen zu ermöglichen.

---

## 🚀 Funktionen
- **Patientendaten** (Name, Geburtsdatum, Geschlecht) ➡️ FHIR Patient-Ressourcen  
- **Diagnosen** (ICD-10) ➡️ FHIR Condition-Ressourcen  
- **Therapien & Prozeduren** (OPS) ➡️ FHIR Procedure-Ressourcen  
- **Laborwerte** (LOINC) ➡️ FHIR Observation-Ressourcen  
- **Import & Export** von FHIR-Daten (JSON/XML)  
- *(Optional)* REST-API für Zugriff & Verwaltung  

---

## 🛠 Technologien
- **Python** (inkl. `fhir.resources`, `Flask`)  
- **JSON / XML** für Datenaustausch  
- **SQLite** als optionale lokale Datenbank  

---

## 📦 Installation

### Option 1: Docker (Empfohlen)

**Voraussetzungen:**
- Docker & Docker Compose installiert ([Installation](https://docs.docker.com/get-docker/))

#### Lokale Entwicklung mit Docker Compose

```bash
# Repository klonen
git clone https://github.com/jamil1230-ln/FHIR-MEDICAL-DATA-TRANSFORMER.git
cd FHIR-MEDICAL-DATA-TRANSFORMER

# Datenverzeichnis erstellen
mkdir -p data

# Services starten
docker compose up -d

# Logs anzeigen
docker compose logs -f fhir-app

# Services stoppen
docker compose down
```

Die Anwendung läuft auf **http://localhost:5000**

#### Production-Deployment mit Docker

```bash
# Docker Image bauen
docker build -t fhir-medical-transformer:latest .

# Container starten
docker run -d \
  --name fhir-transformer \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  fhir-medical-transformer:latest

# Health-Check prüfen
curl http://localhost:5000/api/ping

# Container stoppen
docker stop fhir-transformer
docker rm fhir-transformer
```

**Umgebungsvariablen für Production:**
- `FLASK_ENV=production` - Production-Modus
- `FLASK_DEBUG=0` - Debug-Modus deaktiviert

### Option 2: Manuelle Installation

```bash
# Repository klonen
git clone https://github.com/jamil1230-ln/FHIR-MEDICAL-DATA-TRANSFORMER.git
cd FHIR-MEDICAL-DATA-TRANSFORMER

# Virtuelle Umgebung erstellen & aktivieren
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
python app.py
```

---

## 🐳 Docker-Details

### Image-Optimierungen
- **Multi-Stage Build** für minimale Image-Größe
- **Non-Root User** für erhöhte Sicherheit
- **Health-Checks** für Container-Überwachung
- **Python 3.12 Slim** als Basis-Image

### Optionale Services (docker-compose.yml)

Die `docker-compose.yml` enthält optional konfigurierbare Services:

```yaml
# PostgreSQL-Datenbank (anstelle von SQLite)
# Kommentieren Sie die postgres- und pgadmin-Services aus

# pgAdmin für Datenbank-Management
# Zugriff auf http://localhost:5050
```

### Health-Check Endpoint
```bash
# Prüfen ob der Service läuft
curl http://localhost:5000/api/ping

# Erwartete Antwort:
# {"status": "ok"}
```

### Persistente Daten
Daten werden im Verzeichnis `./data` gespeichert und als Volume gemountet:
- SQLite-Datenbank: `./data/data.db`

---

## 🚀 API-Nutzung

### Health-Check
```bash
curl http://localhost:5000/api/ping
```

### FHIR-Transformation
```bash
curl -X POST http://localhost:5000/api/transform \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "vorname": "Max",
      "nachname": "Mustermann",
      "geburtsdatum": "1980-01-01",
      "geschlecht": "male"
    },
    "diagnosen": [
      {
        "icd10": "E11.9",
        "beschreibung": "Diabetes mellitus Typ 2",
        "klinischer_status": "active"
      }
    ],
    "laborwerte": [
      {
        "loinc": "2339-0",
        "wert": 120.5,
        "einheit": "mg/dL",
        "beschreibung": "Glucose"
      }
    ]
  }'
```
