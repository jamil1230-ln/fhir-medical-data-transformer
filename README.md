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
