from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
import re
from exceptions import InvalidInputError

class PatientIn(BaseModel):
    id: Optional[str] = None
    vorname: str
    nachname: str
    geburtsdatum: date
    geschlecht: str  # "male" | "female" | "other" | "unknown"
    
    @field_validator('vorname', 'nachname')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty and has reasonable length."""
        if not v or not v.strip():
            raise ValueError("Name darf nicht leer sein")
        if len(v.strip()) > 100:
            raise ValueError("Name darf maximal 100 Zeichen lang sein")
        return v.strip()
    
    @field_validator('geschlecht')
    @classmethod
    def validate_geschlecht(cls, v: str) -> str:
        """Validate gender is one of the allowed FHIR values."""
        allowed = ["male", "female", "other", "unknown"]
        if v not in allowed:
            raise ValueError(f"Geschlecht muss einer der folgenden Werte sein: {', '.join(allowed)}")
        return v
    
    @field_validator('geburtsdatum')
    @classmethod
    def validate_geburtsdatum(cls, v: date) -> date:
        """Validate birth date is not in the future."""
        if v > date.today():
            raise ValueError("Geburtsdatum darf nicht in der Zukunft liegen")
        # Check if person is not too old (e.g., max 150 years)
        if v.year < date.today().year - 150:
            raise ValueError("Geburtsdatum liegt zu weit in der Vergangenheit")
        return v 

class DiagnoseIn(BaseModel):
    icd10: str
    beschreibung: Optional[str] = None
    begonnen_am: Optional[date] = None
    klinischer_status: Optional[str] = "active"  # active | remission | resolved
    
    @field_validator('icd10')
    @classmethod
    def validate_icd10(cls, v: str) -> str:
        """Validate ICD-10 code format (basic validation)."""
        if not v or not v.strip():
            raise ValueError("ICD-10 Code darf nicht leer sein")
        v = v.strip().upper()
        # Basic ICD-10 format: Letter followed by 2-3 digits, optionally followed by a dot and more digits
        if not re.match(r'^[A-Z]\d{2,3}(\.\d+)?$', v):
            raise ValueError(f"Ungültiges ICD-10 Format: {v}. Erwartet: z.B. 'A01' oder 'I10.0'")
        return v
    
    @field_validator('klinischer_status')
    @classmethod
    def validate_klinischer_status(cls, v: str) -> str:
        """Validate clinical status."""
        allowed = ["active", "remission", "resolved", "inactive"]
        if v not in allowed:
            raise ValueError(f"Klinischer Status muss einer der folgenden Werte sein: {', '.join(allowed)}")
        return v
    
    @field_validator('begonnen_am')
    @classmethod
    def validate_begonnen_am(cls, v: Optional[date]) -> Optional[date]:
        """Validate start date is not in the future."""
        if v and v > date.today():
            raise ValueError("Beginn der Diagnose darf nicht in der Zukunft liegen")
        return v

class ProzedurIn(BaseModel):
    ops: str
    beschreibung: Optional[str] = None
    datum: Optional[date] = None
    
    @field_validator('ops')
    @classmethod
    def validate_ops(cls, v: str) -> str:
        """Validate OPS code format (basic validation)."""
        if not v or not v.strip():
            raise ValueError("OPS Code darf nicht leer sein")
        v = v.strip().upper()
        # Basic OPS format: 1-2 digits followed by a dash and more digits/letters
        if not re.match(r'^\d{1,2}-\d{2,3}(\.\w+)?$', v):
            raise ValueError(f"Ungültiges OPS Format: {v}. Erwartet: z.B. '5-01' oder '1-23.4'")
        return v
    
    @field_validator('datum')
    @classmethod
    def validate_datum(cls, v: Optional[date]) -> Optional[date]:
        """Validate procedure date is not in the future."""
        if v and v > date.today():
            raise ValueError("Prozedur-Datum darf nicht in der Zukunft liegen")
        return v

class LaborwertIn(BaseModel):
    loinc: str
    wert: float
    einheit: str
    gemessen_am: datetime = Field(default_factory=datetime.utcnow)
    referenz_min: Optional[float] = None
    referenz_max: Optional[float] = None
    beschreibung: Optional[str] = None
    
    @field_validator('loinc')
    @classmethod
    def validate_loinc(cls, v: str) -> str:
        """Validate LOINC code format (basic validation)."""
        if not v or not v.strip():
            raise ValueError("LOINC Code darf nicht leer sein")
        v = v.strip()
        # Basic LOINC format: digits followed by dash and digit
        if not re.match(r'^\d{4,5}-\d$', v):
            raise ValueError(f"Ungültiges LOINC Format: {v}. Erwartet: z.B. '1234-5' oder '12345-6'")
        return v
    
    @field_validator('einheit')
    @classmethod
    def validate_einheit(cls, v: str) -> str:
        """Validate unit is not empty."""
        if not v or not v.strip():
            raise ValueError("Einheit darf nicht leer sein")
        return v.strip()
    
    @field_validator('gemessen_am')
    @classmethod
    def validate_gemessen_am(cls, v: datetime) -> datetime:
        """Validate measurement date is not in the future."""
        if v > datetime.utcnow():
            raise ValueError("Messzeitpunkt darf nicht in der Zukunft liegen")
        return v
    
    @field_validator('referenz_max')
    @classmethod
    def validate_referenz_range(cls, v: Optional[float], info) -> Optional[float]:
        """Validate that reference max is greater than min if both are provided."""
        if v is not None and 'referenz_min' in info.data and info.data['referenz_min'] is not None:
            if v <= info.data['referenz_min']:
                raise ValueError("Referenz-Maximum muss größer als Referenz-Minimum sein")
        return v

class TransformInput(BaseModel):
    patient: PatientIn
    diagnosen: List[DiagnoseIn] = []
    prozeduren: List[ProzedurIn] = []
    laborwerte: List[LaborwertIn] = []
