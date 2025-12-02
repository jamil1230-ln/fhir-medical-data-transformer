"""
Tests for error handling and input validation in FHIR Medical Data Transformer.
"""
import pytest
from datetime import date, datetime
from pydantic import ValidationError

from models import PatientIn, DiagnoseIn, ProzedurIn, LaborwertIn, TransformInput
from exceptions import (
    FHIRTransformerError,
    InvalidInputError,
    FHIRValidationError,
    ResourceCreationError,
    DatabaseError
)


class TestPatientValidation:
    """Test PatientIn model validation."""
    
    def test_valid_patient(self):
        """Test creating a valid patient."""
        patient = PatientIn(
            vorname="Max",
            nachname="Mustermann",
            geburtsdatum=date(1990, 1, 1),
            geschlecht="male"
        )
        assert patient.vorname == "Max"
        assert patient.nachname == "Mustermann"
        assert patient.geschlecht == "male"
    
    def test_invalid_geschlecht(self):
        """Test that invalid geschlecht is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PatientIn(
                vorname="Max",
                nachname="Mustermann",
                geburtsdatum=date(1990, 1, 1),
                geschlecht="invalid"
            )
        assert "geschlecht" in str(exc_info.value).lower()
    
    def test_future_birth_date(self):
        """Test that future birth date is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PatientIn(
                vorname="Max",
                nachname="Mustermann",
                geburtsdatum=date(2030, 1, 1),
                geschlecht="male"
            )
        assert "zukunft" in str(exc_info.value).lower()
    
    def test_empty_name(self):
        """Test that empty names are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PatientIn(
                vorname="",
                nachname="Mustermann",
                geburtsdatum=date(1990, 1, 1),
                geschlecht="male"
            )
        assert "leer" in str(exc_info.value).lower()
    
    def test_all_geschlecht_values(self):
        """Test all valid geschlecht values."""
        for geschlecht in ["male", "female", "other", "unknown"]:
            patient = PatientIn(
                vorname="Test",
                nachname="Person",
                geburtsdatum=date(1990, 1, 1),
                geschlecht=geschlecht
            )
            assert patient.geschlecht == geschlecht


class TestDiagnoseValidation:
    """Test DiagnoseIn model validation."""
    
    def test_valid_icd10_formats(self):
        """Test various valid ICD-10 formats."""
        valid_codes = ["A01", "I10", "E11.9", "C50.1", "J44"]
        for code in valid_codes:
            diag = DiagnoseIn(icd10=code)
            assert diag.icd10 == code.upper()
    
    def test_invalid_icd10(self):
        """Test that invalid ICD-10 codes are rejected."""
        invalid_codes = ["invalid", "1234", "AA", ""]
        for code in invalid_codes:
            with pytest.raises(ValidationError):
                DiagnoseIn(icd10=code)
    
    def test_valid_klinischer_status(self):
        """Test valid clinical status values."""
        valid_statuses = ["active", "remission", "resolved", "inactive"]
        for status in valid_statuses:
            diag = DiagnoseIn(icd10="I10", klinischer_status=status)
            assert diag.klinischer_status == status
    
    def test_invalid_klinischer_status(self):
        """Test that invalid clinical status is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            DiagnoseIn(icd10="I10", klinischer_status="invalid")
        assert "status" in str(exc_info.value).lower()
    
    def test_future_begonnen_am(self):
        """Test that future diagnosis start date is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            DiagnoseIn(icd10="I10", begonnen_am=date(2030, 1, 1))
        assert "zukunft" in str(exc_info.value).lower()


class TestProzedurValidation:
    """Test ProzedurIn model validation."""
    
    def test_valid_ops_formats(self):
        """Test various valid OPS formats."""
        valid_codes = ["5-01", "1-23", "8-123", "5-01.1", "1-23.AB"]
        for code in valid_codes:
            proc = ProzedurIn(ops=code)
            assert proc.ops == code.upper()
    
    def test_invalid_ops(self):
        """Test that invalid OPS codes are rejected."""
        invalid_codes = ["invalid", "A-12", "123", ""]
        for code in invalid_codes:
            with pytest.raises(ValidationError):
                ProzedurIn(ops=code)
    
    def test_future_datum(self):
        """Test that future procedure date is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ProzedurIn(ops="5-01", datum=date(2030, 1, 1))
        assert "zukunft" in str(exc_info.value).lower()


class TestLaborwertValidation:
    """Test LaborwertIn model validation."""
    
    def test_valid_loinc_formats(self):
        """Test various valid LOINC formats."""
        valid_codes = ["1234-5", "12345-6", "9999-0"]
        for code in valid_codes:
            lab = LaborwertIn(loinc=code, wert=100.0, einheit="mg/dL")
            assert lab.loinc == code
    
    def test_invalid_loinc(self):
        """Test that invalid LOINC codes are rejected."""
        invalid_codes = ["invalid", "123-4", "123456-7", ""]
        for code in invalid_codes:
            with pytest.raises(ValidationError):
                LaborwertIn(loinc=code, wert=100.0, einheit="mg/dL")
    
    def test_empty_einheit(self):
        """Test that empty unit is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            LaborwertIn(loinc="1234-5", wert=100.0, einheit="")
        assert "leer" in str(exc_info.value).lower()
    
    def test_future_gemessen_am(self):
        """Test that future measurement date is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            LaborwertIn(
                loinc="1234-5",
                wert=100.0,
                einheit="mg/dL",
                gemessen_am=datetime(2030, 1, 1)
            )
        assert "zukunft" in str(exc_info.value).lower()
    
    def test_invalid_referenz_range(self):
        """Test that invalid reference range is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            LaborwertIn(
                loinc="1234-5",
                wert=100.0,
                einheit="mg/dL",
                referenz_min=150.0,
                referenz_max=100.0
            )
        assert "maximum" in str(exc_info.value).lower()


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_base_exception(self):
        """Test base FHIRTransformerError."""
        exc = FHIRTransformerError("Test error", {"detail": "test"})
        assert exc.message == "Test error"
        assert exc.details == {"detail": "test"}
        
        exc_dict = exc.to_dict()
        assert exc_dict["error"] == "FHIRTransformerError"
        assert exc_dict["message"] == "Test error"
        assert exc_dict["details"] == {"detail": "test"}
    
    def test_invalid_input_error(self):
        """Test InvalidInputError."""
        exc = InvalidInputError("Invalid input")
        assert isinstance(exc, FHIRTransformerError)
        assert exc.message == "Invalid input"
    
    def test_fhir_validation_error(self):
        """Test FHIRValidationError."""
        exc = FHIRValidationError("FHIR validation failed")
        assert isinstance(exc, FHIRTransformerError)
        assert exc.message == "FHIR validation failed"
    
    def test_resource_creation_error(self):
        """Test ResourceCreationError."""
        exc = ResourceCreationError("Resource creation failed")
        assert isinstance(exc, FHIRTransformerError)
        assert exc.message == "Resource creation failed"
    
    def test_database_error(self):
        """Test DatabaseError."""
        exc = DatabaseError("Database operation failed")
        assert isinstance(exc, FHIRTransformerError)
        assert exc.message == "Database operation failed"


class TestTransformInput:
    """Test TransformInput model."""
    
    def test_valid_transform_input(self):
        """Test creating valid transform input."""
        inp = TransformInput(
            patient=PatientIn(
                vorname="Max",
                nachname="Mustermann",
                geburtsdatum=date(1990, 1, 1),
                geschlecht="male"
            ),
            diagnosen=[
                DiagnoseIn(icd10="I10", beschreibung="Hypertonie")
            ],
            prozeduren=[
                ProzedurIn(ops="5-01", beschreibung="Test")
            ],
            laborwerte=[
                LaborwertIn(loinc="1234-5", wert=100.0, einheit="mg/dL")
            ]
        )
        assert inp.patient.vorname == "Max"
        assert len(inp.diagnosen) == 1
        assert len(inp.prozeduren) == 1
        assert len(inp.laborwerte) == 1
    
    def test_empty_lists(self):
        """Test that empty lists are allowed."""
        inp = TransformInput(
            patient=PatientIn(
                vorname="Max",
                nachname="Mustermann",
                geburtsdatum=date(1990, 1, 1),
                geschlecht="male"
            )
        )
        assert inp.diagnosen == []
        assert inp.prozeduren == []
        assert inp.laborwerte == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
