# FHIR Medical Data Transformer

Ein **Python-basiertes Tool** zur Transformation medizinischer Rohdaten in das standardisierte **FHIR-Format** (Fast Healthcare Interoperability Resources).

Das Tool verarbeitet medizinische Textdaten und Codes (z. B. **ICD-10**, **OPS**, **LOINC**) und wandelt sie in strukturierte FHIR-Ressourcen um, um die interoperable Übertragung von Patientendaten, Diagnosen, Therapieplänen, Laborwerten und Bildgebungsinformationen zwischen verschiedenen Gesundheitssystemen zu ermöglichen.

---

## 📋 Inhaltsverzeichnis
- [Funktionen](#-funktionen)
- [Architektur](#-architektur)
- [Technologien](#-technologien)
- [Voraussetzungen](#-voraussetzungen)
- [Installation](#-installation)
- [Konfiguration](#-konfiguration)
- [Verwendung](#-verwendung)
  - [Server starten](#server-starten)
  - [API-Endpunkte](#api-endpunkte)
  - [Verwendungsbeispiele](#verwendungsbeispiele)
- [API-Dokumentation](#-api-dokumentation)
- [FHIR-Ressourcentypen](#-fhir-ressourcentypen)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Mitwirken](#-mitwirken)
- [Lizenz](#-lizenz)

---

## 🚀 Funktionen

### Unterstützte Transformationen
- **Patientendaten** (Name, Geburtsdatum, Geschlecht) ➡️ FHIR Patient-Ressourcen  
- **Diagnosen** (ICD-10) ➡️ FHIR Condition-Ressourcen  
- **Therapien & Prozeduren** (OPS) ➡️ FHIR Procedure-Ressourcen  
- **Laborwerte** (LOINC) ➡️ FHIR Observation-Ressourcen  

### Hauptmerkmale
- ✅ **REST-API** für einfache Integration
- ✅ **FHIR R4** Standard-Konformität
- ✅ **Automatische Validierung** der Eingabedaten mit Pydantic
- ✅ **Persistierung** der generierten FHIR-Bundles in SQLite
- ✅ **UUID-basierte IDs** für alle Ressourcen
- ✅ **Referenzierung** zwischen Ressourcen (Patient → Condition/Procedure/Observation)
- ✅ **Codierung** mit standardisierten Terminologien (ICD-10, OPS, LOINC)
- ✅ **Metadaten** und Zeitstempel für Nachvollziehbarkeit

---

## 🏗 Architektur

Das System besteht aus mehreren Modulen:

```
fhir-medical-data-transformer/
├── app.py              # Flask REST-API Server
├── models.py           # Pydantic-Datenmodelle für Input-Validierung
├── fhir_handler.py     # FHIR-Transformationslogik
├── database.py         # SQLite-Datenbankanbindung
├── requirements.txt    # Python-Abhängigkeiten
└── README.md          # Dokumentation
```

**Datenfluss:**
1. Client sendet JSON-Daten an `/api/transform`
2. Pydantic validiert die Eingabe (models.py)
3. FHIR-Handler erstellt FHIR-Ressourcen (fhir_handler.py)
4. Bundle wird in SQLite gespeichert (database.py)
5. FHIR-Bundle wird als JSON zurückgegeben

---

## 🛠 Technologien

- **Python 3.12+** - Programmiersprache
- **Flask 3.1** - Web-Framework für REST-API
- **fhir.resources 8.1** - FHIR R4 Ressourcen-Modelle
- **Pydantic 2.11** - Datenvalidierung
- **SQLAlchemy 2.0** - Datenbank-ORM
- **SQLite** - Lokale Datenbank
- **pytest** - Testing-Framework
- **Flask-CORS** - Cross-Origin Resource Sharing
- **loguru** - Logging-Bibliothek

---

## ✅ Voraussetzungen

- **Python 3.9 oder höher** (empfohlen: Python 3.12)
- **pip** (Python Package Manager)
- **virtualenv** (optional, aber empfohlen)
- **Git** (zum Klonen des Repositories)

---

## 📦 Installation

### 1. Repository klonen

```bash
git clone https://github.com/jamil1230-ln/fhir-medical-data-transformer.git
cd fhir-medical-data-transformer
```

### 2. Virtuelle Umgebung erstellen und aktivieren

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Abhängigkeiten installieren

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Datenbank initialisieren (optional)

Die Datenbank wird automatisch beim ersten API-Aufruf erstellt. Sie können sie aber auch manuell initialisieren:

```bash
python -c "from database import init_db; init_db()"
```

---

## ⚙️ Konfiguration

### Umgebungsvariablen

Erstellen Sie eine `.env`-Datei im Projektverzeichnis (siehe `.env.example`):

```bash
# Flask-Konfiguration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Datenbank
DATABASE_URL=sqlite:///data.db

# CORS
CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO
```

---

## 💻 Verwendung

### Server starten

**Entwicklungsmodus:**
```bash
python app.py
```

Der Server läuft dann auf `http://127.0.0.1:5000`

**Produktionsmodus mit Gunicorn:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### API-Endpunkte

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/ping` | Health-Check |
| POST | `/api/transform` | Transformiert medizinische Daten zu FHIR-Bundle |

### Verwendungsbeispiele

#### 1. Health-Check

```bash
curl http://localhost:5000/api/ping
```

**Response:**
```json
{
  "status": "ok"
}
```

#### 2. Vollständige Transformation (alle Ressourcentypen)

```bash
curl -X POST http://localhost:5000/api/transform \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "vorname": "Max",
      "nachname": "Mustermann",
      "geburtsdatum": "1985-05-15",
      "geschlecht": "male"
    },
    "diagnosen": [
      {
        "icd10": "E11.9",
        "beschreibung": "Diabetes mellitus Typ 2 ohne Komplikationen",
        "begonnen_am": "2023-01-15",
        "klinischer_status": "active"
      }
    ],
    "prozeduren": [
      {
        "ops": "1-471",
        "beschreibung": "Biopsie ohne Inzision am Endokard",
        "datum": "2023-02-20"
      }
    ],
    "laborwerte": [
      {
        "loinc": "2339-0",
        "beschreibung": "Glukose im Blut",
        "wert": 126.5,
        "einheit": "mg/dL",
        "gemessen_am": "2023-03-10T08:30:00",
        "referenz_min": 70.0,
        "referenz_max": 100.0
      }
    ]
  }'
```

#### 3. Nur Patientendaten (minimal)

```bash
curl -X POST http://localhost:5000/api/transform \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "vorname": "Anna",
      "nachname": "Schmidt",
      "geburtsdatum": "1990-03-20",
      "geschlecht": "female"
    }
  }'
```

#### 4. Patient mit mehreren Diagnosen

```bash
curl -X POST http://localhost:5000/api/transform \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "vorname": "Hans",
      "nachname": "Meier",
      "geburtsdatum": "1970-07-10",
      "geschlecht": "male"
    },
    "diagnosen": [
      {
        "icd10": "I10",
        "beschreibung": "Essentielle (primäre) Hypertonie",
        "begonnen_am": "2020-01-01",
        "klinischer_status": "active"
      },
      {
        "icd10": "E78.0",
        "beschreibung": "Reine Hypercholesterinämie",
        "begonnen_am": "2021-06-15",
        "klinischer_status": "active"
      }
    ]
  }'
```

#### 5. Patient mit Laborwerten

```bash
curl -X POST http://localhost:5000/api/transform \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "vorname": "Maria",
      "nachname": "Müller",
      "geburtsdatum": "1988-11-25",
      "geschlecht": "female"
    },
    "laborwerte": [
      {
        "loinc": "2093-3",
        "beschreibung": "Cholesterin im Serum",
        "wert": 220.0,
        "einheit": "mg/dL",
        "gemessen_am": "2024-01-15T09:00:00",
        "referenz_min": 0.0,
        "referenz_max": 200.0
      },
      {
        "loinc": "2085-9",
        "beschreibung": "HDL-Cholesterin im Serum",
        "wert": 45.0,
        "einheit": "mg/dL",
        "gemessen_am": "2024-01-15T09:00:00",
        "referenz_min": 40.0,
        "referenz_max": 60.0
      }
    ]
  }'
```

#### 6. Patient mit Prozeduren

```bash
curl -X POST http://localhost:5000/api/transform \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "vorname": "Peter",
      "nachname": "Wagner",
      "geburtsdatum": "1965-04-30",
      "geschlecht": "male"
    },
    "prozeduren": [
      {
        "ops": "5-470",
        "beschreibung": "Appendektomie",
        "datum": "2023-08-10"
      },
      {
        "ops": "8-930",
        "beschreibung": "Monitoring von Atmung, Herz und Kreislauf",
        "datum": "2023-08-11"
      }
    ]
  }'
```

---

## 📚 API-Dokumentation

### POST `/api/transform`

Transformiert medizinische Rohdaten in ein FHIR R4 Bundle.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body Schema:**

```json
{
  "patient": {
    "id": "string (optional)",
    "vorname": "string (required)",
    "nachname": "string (required)",
    "geburtsdatum": "date (required, Format: YYYY-MM-DD)",
    "geschlecht": "string (required, 'male' oder 'female')"
  },
  "diagnosen": [
    {
      "icd10": "string (required)",
      "beschreibung": "string (optional)",
      "begonnen_am": "date (optional, Format: YYYY-MM-DD)",
      "klinischer_status": "string (optional, default: 'active')"
    }
  ],
  "prozeduren": [
    {
      "ops": "string (required)",
      "beschreibung": "string (optional)",
      "datum": "date (optional, Format: YYYY-MM-DD)"
    }
  ],
  "laborwerte": [
    {
      "loinc": "string (required)",
      "beschreibung": "string (optional)",
      "wert": "number (required)",
      "einheit": "string (required)",
      "gemessen_am": "datetime (optional, Format: ISO 8601)",
      "referenz_min": "number (optional)",
      "referenz_max": "number (optional)"
    }
  ]
}
```

#### Response

**Status: 201 Created**

**Body:** FHIR R4 Bundle (JSON)

```json
{
  "resourceType": "Bundle",
  "id": "bundle-{uuid}",
  "type": "collection",
  "timestamp": "2024-01-15T10:30:00.000000",
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "pat-{uuid}",
        "meta": {
          "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
        },
        "name": [
          {
            "family": "Mustermann",
            "given": ["Max"]
          }
        ],
        "gender": "male",
        "birthDate": "1985-05-15"
      }
    },
    {
      "resource": {
        "resourceType": "Condition",
        "id": "cond-{uuid}",
        "subject": {
          "reference": "Patient/pat-{uuid}"
        },
        "code": {
          "coding": [
            {
              "system": "http://hl7.org/fhir/sid/icd-10",
              "code": "E11.9",
              "display": "Diabetes mellitus Typ 2 ohne Komplikationen"
            }
          ],
          "text": "Diabetes mellitus Typ 2 ohne Komplikationen"
        },
        "clinicalStatus": {
          "text": "active"
        },
        "onsetDateTime": "2023-01-15"
      }
    },
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "proc-{uuid}",
        "status": "completed",
        "subject": {
          "reference": "Patient/pat-{uuid}"
        },
        "code": {
          "coding": [
            {
              "system": "http://fhir.de/CodeSystem/dimdi/ops",
              "code": "1-471",
              "display": "Biopsie ohne Inzision am Endokard"
            }
          ],
          "text": "Biopsie ohne Inzision am Endokard"
        },
        "performedDateTime": "2023-02-20"
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "obs-{uuid}",
        "status": "final",
        "category": [
          {
            "text": "laboratory"
          }
        ],
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "2339-0",
              "display": "Glukose im Blut"
            }
          ],
          "text": "Glukose im Blut"
        },
        "subject": {
          "reference": "Patient/pat-{uuid}"
        },
        "effectiveDateTime": "2023-03-10T08:30:00",
        "valueQuantity": {
          "value": 126.5,
          "unit": "mg/dL"
        },
        "referenceRange": [
          {
            "low": {
              "value": 70.0,
              "unit": "mg/dL"
            },
            "high": {
              "value": 100.0,
              "unit": "mg/dL"
            }
          }
        ]
      }
    }
  ]
}
```

**Fehlerresponse:**

**Status: 400 Bad Request**

```json
{
  "error": "Detailed error message"
}
```

**Mögliche Fehler:**
- Fehlende oder ungültige Pflichtfelder
- Ungültige Datumsformate
- Ungültige Geschlechtsangaben
- JSON-Parsing-Fehler

---

## 🧬 FHIR-Ressourcentypen

### Patient Resource
- **System:** FHIR R4
- **Profile:** `http://hl7.org/fhir/StructureDefinition/Patient`
- **Pflichtfelder:** name, gender, birthDate

### Condition Resource (Diagnosen)
- **Coding System:** ICD-10 (`http://hl7.org/fhir/sid/icd-10`)
- **Referenz:** Patient
- **Status:** clinicalStatus (active, remission, resolved)

### Procedure Resource (Prozeduren)
- **Coding System:** OPS (`http://fhir.de/CodeSystem/dimdi/ops`)
- **Referenz:** Patient
- **Status:** completed (default)

### Observation Resource (Laborwerte)
- **Coding System:** LOINC (`http://loinc.org`)
- **Referenz:** Patient
- **Category:** laboratory
- **Status:** final
- **valueQuantity:** Messwert mit Einheit
- **referenceRange:** Referenzbereich (optional)

---

## 🚀 Deployment

### Lokal (Entwicklung)

```bash
python app.py
```

### Docker

**Dockerfile erstellen:**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

**Container bauen und starten:**

```bash
docker build -t fhir-transformer .
docker run -p 5000:5000 -v $(pwd)/data.db:/app/data.db fhir-transformer
```

### Docker Compose

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  fhir-transformer:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data.db:/app/data.db
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
    restart: unless-stopped
```

**Starten:**

```bash
docker-compose up -d
```

### Produktion (mit Nginx als Reverse Proxy)

**1. Gunicorn installieren:**

```bash
pip install gunicorn
```

**2. Gunicorn-Service erstellen (`/etc/systemd/system/fhir-transformer.service`):**

```ini
[Unit]
Description=FHIR Medical Data Transformer
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/fhir-transformer
Environment="PATH=/opt/fhir-transformer/venv/bin"
ExecStart=/opt/fhir-transformer/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

**3. Service aktivieren:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable fhir-transformer
sudo systemctl start fhir-transformer
```

**4. Nginx-Konfiguration (`/etc/nginx/sites-available/fhir-transformer`):**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**5. Nginx aktivieren:**

```bash
sudo ln -s /etc/nginx/sites-available/fhir-transformer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Cloud-Deployment (Heroku)

**1. Procfile erstellen:**

```
web: gunicorn app:app
```

**2. Deployment:**

```bash
heroku create fhir-transformer-app
git push heroku main
heroku open
```

---

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'fhir'"

**Lösung:**
```bash
pip install --upgrade fhir.resources
```

### Problem: "sqlite3.OperationalError: no such table: bundles"

**Lösung:**
```bash
python -c "from database import init_db; init_db()"
```

### Problem: "Address already in use"

**Lösung:**
```bash
# Port 5000 ist bereits belegt, anderen Port verwenden
export FLASK_PORT=5001
python app.py
```

oder den Prozess stoppen:

```bash
lsof -ti:5000 | xargs kill -9
```

### Problem: "Connection refused"

**Lösung:**
- Stellen Sie sicher, dass der Server läuft
- Prüfen Sie Firewall-Einstellungen
- Verwenden Sie die richtige URL (http://localhost:5000)

### Problem: Validierungsfehler bei Datumsangaben

**Lösung:**
- Verwenden Sie ISO-Format: `YYYY-MM-DD` für Daten
- Verwenden Sie ISO 8601 für Zeitstempel: `YYYY-MM-DDTHH:MM:SS`

---

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte lesen Sie [CONTRIBUTING.md](CONTRIBUTING.md) für Details zum Prozess.

### Entwicklungsumgebung einrichten

1. Repository forken
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request öffnen

### Tests ausführen

```bash
pytest
```

### Code-Stil

- PEP 8 für Python-Code
- Type Hints verwenden
- Docstrings für Funktionen und Klassen

---

## 📄 Lizenz

Dieses Projekt ist lizenziert unter der MIT-Lizenz.

---

## 📞 Kontakt

- **GitHub:** [@jamil1230-ln](https://github.com/jamil1230-ln)
- **Repository:** [fhir-medical-data-transformer](https://github.com/jamil1230-ln/fhir-medical-data-transformer)

---

## 🙏 Danksagungen

- [HL7 FHIR](https://www.hl7.org/fhir/) für den FHIR-Standard
- [fhir.resources](https://github.com/nazrulworld/fhir.resources) Python-Bibliothek
- [Flask](https://flask.palletsprojects.com/) Web-Framework
