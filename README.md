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
```bash
# Repository klonen
git clone https://github.com/jamil1230-ln/FHIR-MEDICAL-DATA-TRANSFORMER.git
cd FHIR-MEDICAL-DATA-TRANSFORMER

# Virtuelle Umgebung erstellen & aktivieren
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

---

## 🧪 Tests & CI/CD

### Automatisierte Tests
Das Projekt verwendet **pytest** für automatisierte Tests. Um Tests lokal auszuführen:

```bash
# Alle Tests ausführen
pytest

# Tests mit Coverage-Report
pytest --cov=. --cov-report=term-missing

# Bestimmte Testdatei ausführen
pytest tests/test_api.py
```

### GitHub Actions Workflows

Das Projekt nutzt GitHub Actions für kontinuierliche Integration und Code-Qualitätsprüfungen:

#### 1. **Tests Workflow** (`.github/workflows/tests.yml`)
- Läuft bei jedem Push und Pull Request auf `main` und `develop` Branches
- Testet Python-Versionen: 3.9, 3.10, 3.11, 3.12
- Führt folgende Schritte aus:
  - Installation der Abhängigkeiten
  - Linting mit **flake8**
  - Ausführung aller Tests mit **pytest**
  - Code-Coverage-Reporting
  - Upload zu Codecov (optional)

#### 2. **Code Quality Workflow** (`.github/workflows/code-quality.yml`)
- Läuft bei jedem Push und Pull Request auf `main` und `develop` Branches
- Enthält zwei Jobs:
  - **Pre-commit Checks**: Formatierung, Linting, und Best Practices
  - **Security Checks**: Sicherheitsprüfungen mit **Bandit** und **Safety**

### Pre-commit Hooks
Pre-commit Hooks werden automatisch vor jedem Commit ausgeführt:

```bash
# Pre-commit installieren
pip install pre-commit

# Hooks einrichten
pre-commit install

# Manuell alle Dateien prüfen
pre-commit run --all-files
```

Die Hooks führen folgende Prüfungen durch:
- Code-Formatierung mit **black**
- Import-Sortierung mit **isort**
- Linting mit **flake8**
- Sicherheitsprüfungen mit **bandit**
- Entfernung von trailing whitespaces
- Validierung von YAML/JSON-Dateien

