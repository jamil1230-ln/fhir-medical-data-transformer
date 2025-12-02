"""Basic tests for FHIR Medical Data Transformer."""

from datetime import date, datetime
import pytest
from models import PatientIn, DiagnoseIn, ProzedurIn, LaborwertIn, TransformInput
from fhir_handler import transform_to_fhir_bundle


class TestModels:
    """Test Pydantic models."""

    def test_patient_in_creation(self):
        """Test PatientIn model creation."""
        patient = PatientIn(
            vorname="Max",
            nachname="Mustermann",
            geburtsdatum=date(1980, 1, 1),
            geschlecht="male"
        )
        assert patient.vorname == "Max"
        assert patient.nachname == "Mustermann"
        assert patient.geschlecht == "male"

    def test_diagnose_in_creation(self):
        """Test DiagnoseIn model creation."""
        diagnose = DiagnoseIn(
            icd10="E11.9",
            beschreibung="Diabetes mellitus"
        )
        assert diagnose.icd10 == "E11.9"
        assert diagnose.klinischer_status == "active"

    def test_prozedur_in_creation(self):
        """Test ProzedurIn model creation."""
        prozedur = ProzedurIn(
            ops="5-470",
            beschreibung="Appendektomie"
        )
        assert prozedur.ops == "5-470"
        assert prozedur.beschreibung == "Appendektomie"

    def test_laborwert_in_creation(self):
        """Test LaborwertIn model creation."""
        laborwert = LaborwertIn(
            loinc="2339-0",
            wert=5.5,
            einheit="mmol/L"
        )
        assert laborwert.loinc == "2339-0"
        assert laborwert.wert == 5.5


class TestFHIRTransformation:
    """Test FHIR transformation functions."""

    def test_transform_to_fhir_bundle_basic(self):
        """Test basic FHIR bundle transformation."""
        transform_input = TransformInput(
            patient=PatientIn(
                vorname="Max",
                nachname="Mustermann",
                geburtsdatum=date(1980, 1, 1),
                geschlecht="male"
            )
        )
        bundle = transform_to_fhir_bundle(transform_input)
        
        assert bundle.get_resource_type() == "Bundle"
        assert bundle.type == "collection"
        assert len(bundle.entry) == 1
        assert bundle.entry[0]["resource"].get_resource_type() == "Patient"

    def test_transform_with_diagnose(self):
        """Test FHIR transformation with diagnosis."""
        transform_input = TransformInput(
            patient=PatientIn(
                vorname="Max",
                nachname="Mustermann",
                geburtsdatum=date(1980, 1, 1),
                geschlecht="male"
            ),
            diagnosen=[
                DiagnoseIn(
                    icd10="E11.9",
                    beschreibung="Diabetes mellitus"
                )
            ]
        )
        bundle = transform_to_fhir_bundle(transform_input)
        
        assert len(bundle.entry) == 2
        assert bundle.entry[0]["resource"].get_resource_type() == "Patient"
        assert bundle.entry[1]["resource"].get_resource_type() == "Condition"

    def test_transform_with_multiple_resources(self):
        """Test FHIR transformation with multiple resources."""
        transform_input = TransformInput(
            patient=PatientIn(
                vorname="Max",
                nachname="Mustermann",
                geburtsdatum=date(1980, 1, 1),
                geschlecht="male"
            ),
            diagnosen=[
                DiagnoseIn(icd10="E11.9", beschreibung="Diabetes mellitus")
            ],
            prozeduren=[
                ProzedurIn(ops="5-470", beschreibung="Appendektomie")
            ],
            laborwerte=[
                LaborwertIn(loinc="2339-0", wert=5.5, einheit="mmol/L")
            ]
        )
        bundle = transform_to_fhir_bundle(transform_input)
        
        # 1 Patient + 1 Condition + 1 Procedure + 1 Observation
        assert len(bundle.entry) == 4
        resource_types = [entry["resource"].get_resource_type() for entry in bundle.entry]
        assert "Patient" in resource_types
        assert "Condition" in resource_types
        assert "Procedure" in resource_types
        assert "Observation" in resource_types
