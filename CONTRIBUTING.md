# Beitragen zum FHIR Medical Data Transformer

Vielen Dank für Ihr Interesse, zum FHIR Medical Data Transformer beizutragen! Wir freuen uns über alle Beiträge - ob Bugfixes, neue Features, Dokumentationsverbesserungen oder Tests.

## 📋 Inhaltsverzeichnis

- [Code of Conduct](#code-of-conduct)
- [Wie kann ich beitragen?](#wie-kann-ich-beitragen)
- [Entwicklungsumgebung einrichten](#entwicklungsumgebung-einrichten)
- [Entwicklungsprozess](#entwicklungsprozess)
- [Code-Standards](#code-standards)
- [Testing](#testing)
- [Pull Request Prozess](#pull-request-prozess)
- [Issue-Richtlinien](#issue-richtlinien)

---

## Code of Conduct

Dieses Projekt folgt dem [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/de/version/2/1/code_of_conduct/). Durch Ihre Teilnahme verpflichten Sie sich, diesen Code einzuhalten. Bitte melden Sie inakzeptables Verhalten an die Projekt-Maintainer.

---

## Wie kann ich beitragen?

### 🐛 Bugs melden

Bugs werden als GitHub Issues verfolgt. Bevor Sie einen Bug melden:

1. **Prüfen Sie**, ob der Bug bereits gemeldet wurde
2. **Stellen Sie sicher**, dass Sie die neueste Version verwenden
3. **Reproduzieren Sie** den Bug mit minimalen Schritten

**Bug-Report sollte enthalten:**

- **Titel:** Kurze, aussagekräftige Beschreibung
- **Beschreibung:** Detaillierte Beschreibung des Problems
- **Reproduktionsschritte:** Schritt-für-Schritt-Anleitung
- **Erwartetes Verhalten:** Was sollte passieren?
- **Tatsächliches Verhalten:** Was passiert stattdessen?
- **Umgebung:** Python-Version, Betriebssystem, etc.
- **Fehlerausgabe:** Vollständige Fehlermeldungen und Stack Traces
- **Screenshots:** Falls relevant

### 💡 Features vorschlagen

Feature-Requests sind ebenfalls willkommen! Bitte:

1. **Prüfen Sie**, ob das Feature bereits vorgeschlagen wurde
2. **Beschreiben Sie** den Use-Case und Nutzen
3. **Erklären Sie**, warum das Feature wichtig ist
4. **Schlagen Sie** eine mögliche Implementierung vor (optional)

### 📝 Dokumentation verbessern

Dokumentationsverbesserungen sind immer willkommen:

- README.md ergänzen oder verbessern
- Code-Kommentare hinzufügen
- API-Dokumentation erweitern
- Tutorials oder Beispiele erstellen
- Tippfehler korrigieren

### 🔧 Code beitragen

1. **Fork** das Repository
2. **Erstellen Sie** einen Feature-Branch
3. **Implementieren Sie** Ihre Änderungen
4. **Testen Sie** Ihren Code
5. **Committen Sie** mit aussagekräftigen Commit-Messages
6. **Pushen Sie** zu Ihrem Fork
7. **Öffnen Sie** einen Pull Request

---

## Entwicklungsumgebung einrichten

### Voraussetzungen

- Python 3.9 oder höher (empfohlen: 3.12)
- Git
- virtualenv oder venv

### Setup

1. **Repository forken und klonen:**

```bash
git clone https://github.com/YOUR-USERNAME/fhir-medical-data-transformer.git
cd fhir-medical-data-transformer
```

2. **Upstream-Remote hinzufügen:**

```bash
git remote add upstream https://github.com/jamil1230-ln/fhir-medical-data-transformer.git
```

3. **Virtuelle Umgebung erstellen:**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

4. **Abhängigkeiten installieren:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Entwicklungs-Dependencies installieren (optional):**

```bash
pip install pytest pytest-cov black flake8 mypy
```

6. **Datenbank initialisieren:**

```bash
python -c "from database import init_db; init_db()"
```

7. **Server testen:**

```bash
python app.py
```

---

## Entwicklungsprozess

### Branch-Strategie

- `main` - Stabile, produktionsreife Version
- `feature/<feature-name>` - Neue Features
- `bugfix/<bug-description>` - Bugfixes
- `docs/<doc-description>` - Dokumentationsänderungen
- `refactor/<refactor-description>` - Code-Refactoring

### Workflow

1. **Branch erstellen:**

```bash
git checkout -b feature/mein-neues-feature
```

2. **Änderungen machen:**

```bash
# Code bearbeiten
# Tests hinzufügen/aktualisieren
```

3. **Änderungen committen:**

```bash
git add .
git commit -m "feat: Beschreibung des Features"
```

4. **Upstream synchronisieren:**

```bash
git fetch upstream
git rebase upstream/main
```

5. **Zu Fork pushen:**

```bash
git push origin feature/mein-neues-feature
```

6. **Pull Request öffnen**

---

## Code-Standards

### Python-Stil

Wir folgen [PEP 8](https://pep8.org/) mit einigen Anpassungen:

- **Zeilenlänge:** Max. 100 Zeichen (statt 79)
- **Imports:** Gruppiert und alphabetisch sortiert
- **Docstrings:** Google-Style für Funktionen und Klassen
- **Type Hints:** Verwenden Sie Type Annotations wo möglich

### Code-Formatierung

Verwenden Sie `black` für automatische Formatierung:

```bash
black .
```

### Linting

Prüfen Sie Ihren Code mit `flake8`:

```bash
flake8 . --max-line-length=100 --exclude=venv,__pycache__
```

### Type-Checking

Verwenden Sie `mypy` für Type-Checking:

```bash
mypy . --ignore-missing-imports
```

### Beispiel: Gut formatierter Code

```python
from typing import Optional, List
from datetime import date
from uuid import uuid4
from pydantic import BaseModel


class PatientIn(BaseModel):
    """
    Pydantic-Modell für Patienteneingabe.
    
    Attributes:
        id: Optional eindeutige Patienten-ID
        vorname: Vorname des Patienten
        nachname: Nachname des Patienten
        geburtsdatum: Geburtsdatum im Format YYYY-MM-DD
        geschlecht: Geschlecht (male oder female)
    """
    id: Optional[str] = None
    vorname: str
    nachname: str
    geburtsdatum: date
    geschlecht: str


def transform_patient(patient: PatientIn) -> dict:
    """
    Transformiert Patientendaten in FHIR-Format.
    
    Args:
        patient: Patienteneingabe-Objekt
        
    Returns:
        FHIR Patient-Ressource als Dictionary
        
    Raises:
        ValueError: Wenn Geschlecht ungültig ist
    """
    if patient.geschlecht not in ["male", "female"]:
        raise ValueError(f"Ungültiges Geschlecht: {patient.geschlecht}")
    
    return {
        "resourceType": "Patient",
        "id": patient.id or f"pat-{uuid4()}",
        "name": [{"family": patient.nachname, "given": [patient.vorname]}],
        "gender": patient.geschlecht,
        "birthDate": str(patient.geburtsdatum)
    }
```

### Commit-Messages

Verwenden Sie [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: Neues Feature
- `fix`: Bugfix
- `docs`: Dokumentationsänderungen
- `style`: Code-Formatierung (keine funktionale Änderung)
- `refactor`: Code-Refactoring
- `test`: Tests hinzufügen/ändern
- `chore`: Build-Prozess, Dependencies, etc.

**Beispiele:**

```
feat(api): Add patient search endpoint

Implemented GET /api/patients endpoint with filtering
by name, birthdate, and gender.

Closes #123
```

```
fix(fhir): Correct ICD-10 system URL

Changed system URL from incorrect value to official
http://hl7.org/fhir/sid/icd-10

Fixes #456
```

```
docs(readme): Add deployment section

Added detailed instructions for Docker and production
deployment with Nginx.
```

---

## Testing

### Tests schreiben

Alle neuen Features und Bugfixes sollten Tests enthalten:

```python
# test_fhir_handler.py
import pytest
from datetime import date
from models import PatientIn
from fhir_handler import _patient_resource


def test_patient_resource_creation():
    """Test dass Patient-Ressource korrekt erstellt wird."""
    patient_in = PatientIn(
        vorname="Max",
        nachname="Mustermann",
        geburtsdatum=date(1985, 5, 15),
        geschlecht="male"
    )
    
    patient = _patient_resource(patient_in)
    
    assert patient.resourceType == "Patient"
    assert patient.name[0].family == "Mustermann"
    assert patient.name[0].given == ["Max"]
    assert patient.gender == "male"
    assert patient.birthDate == "1985-05-15"


def test_patient_resource_with_custom_id():
    """Test dass benutzerdefinierte Patient-ID verwendet wird."""
    patient_in = PatientIn(
        id="custom-123",
        vorname="Anna",
        nachname="Schmidt",
        geburtsdatum=date(1990, 3, 20),
        geschlecht="female"
    )
    
    patient = _patient_resource(patient_in)
    
    assert patient.id == "custom-123"
```

### Tests ausführen

```bash
# Alle Tests
pytest

# Mit Coverage-Report
pytest --cov=. --cov-report=html

# Spezifische Tests
pytest tests/test_fhir_handler.py

# Verbose-Modus
pytest -v
```

### Test-Coverage

Wir streben eine Test-Coverage von mindestens 80% an:

```bash
pytest --cov=. --cov-report=term-missing
```

---

## Pull Request Prozess

### Vor dem Einreichen

**Checkliste:**

- [ ] Code folgt PEP 8 und Projekt-Standards
- [ ] Alle Tests bestehen (`pytest`)
- [ ] Neue Tests für neue Features/Bugfixes hinzugefügt
- [ ] Dokumentation aktualisiert (README, Docstrings, etc.)
- [ ] Type Hints hinzugefügt
- [ ] Code formatiert (`black .`)
- [ ] Linting bestanden (`flake8`)
- [ ] Commit-Messages folgen Conventional Commits
- [ ] Branch ist aktuell mit `main`

### Pull Request Template

Verwenden Sie diese Vorlage für Ihren PR:

```markdown
## Beschreibung

Kurze Beschreibung der Änderungen.

## Motivation und Kontext

Warum ist diese Änderung notwendig? Welches Problem löst sie?

Fixes #(issue-nummer)

## Art der Änderung

- [ ] Bugfix (nicht-breaking change, der einen Fehler behebt)
- [ ] Neues Feature (nicht-breaking change, der Funktionalität hinzufügt)
- [ ] Breaking Change (Änderung, die bestehende Funktionalität beeinträchtigt)
- [ ] Dokumentation

## Tests durchgeführt

Beschreiben Sie, wie Sie Ihre Änderungen getestet haben.

- [ ] Unit Tests hinzugefügt
- [ ] Manuelle Tests durchgeführt
- [ ] Alle bestehenden Tests bestehen

## Screenshots (falls UI-Änderungen)

Fügen Sie relevante Screenshots hinzu.

## Checkliste

- [ ] Code folgt Projekt-Standards
- [ ] Selbst-Review durchgeführt
- [ ] Code ist kommentiert (komplexe Bereiche)
- [ ] Dokumentation aktualisiert
- [ ] Keine neuen Warnings
- [ ] Tests hinzugefügt
- [ ] Alle Tests bestehen
```

### Review-Prozess

1. **Automatische Checks:** GitHub Actions führt Tests und Linting aus
2. **Code-Review:** Mindestens ein Maintainer überprüft den Code
3. **Feedback umsetzen:** Änderungen basierend auf Review-Kommentaren
4. **Approval:** Nach erfolgreicher Review wird der PR genehmigt
5. **Merge:** Maintainer mergt den PR in `main`

---

## Issue-Richtlinien

### Issue-Templates

#### Bug-Report

```markdown
**Beschreibung:**
Kurze Beschreibung des Bugs.

**Reproduktionsschritte:**
1. Schritt 1
2. Schritt 2
3. ...

**Erwartetes Verhalten:**
Was sollte passieren?

**Tatsächliches Verhalten:**
Was passiert stattdessen?

**Umgebung:**
- OS: [z.B. Ubuntu 22.04]
- Python-Version: [z.B. 3.12]
- Projekt-Version: [z.B. 1.0.0]

**Fehlerausgabe:**
```
Fügen Sie vollständige Fehlerausgabe ein
```

**Zusätzlicher Kontext:**
Weitere relevante Informationen.
```

#### Feature-Request

```markdown
**Feature-Beschreibung:**
Was soll implementiert werden?

**Use-Case:**
Warum wird dieses Feature benötigt?

**Vorgeschlagene Lösung:**
Wie könnte das Feature implementiert werden?

**Alternativen:**
Welche Alternativen gibt es?

**Zusätzlicher Kontext:**
Screenshots, Mockups, etc.
```

---

## Fragen?

Falls Sie Fragen haben:

- **GitHub Discussions:** Nutzen Sie GitHub Discussions für allgemeine Fragen
- **Issues:** Öffnen Sie ein Issue für spezifische Probleme
- **Email:** Kontaktieren Sie die Maintainer

---

## Danke!

Vielen Dank für Ihren Beitrag zum FHIR Medical Data Transformer! 🎉

Jeder Beitrag, ob groß oder klein, wird geschätzt und hilft, das Projekt zu verbessern.
