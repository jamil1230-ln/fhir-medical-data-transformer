from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class PatientIn(BaseModel):
    id: Optional[str] = None
    vorname: str
    nachname: str
    geburtsdatum: date
    geschlecht: str  # "male" | "female" 

class DiagnoseIn(BaseModel):
    icd10: str
    beschreibung: Optional[str] = None
    begonnen_am: Optional[date] = None
    klinischer_status: Optional[str] = "active"  # active | remission | resolved

class ProzedurIn(BaseModel):
    ops: str
    beschreibung: Optional[str] = None
    datum: Optional[date] = None

class LaborwertIn(BaseModel):
    loinc: str
    wert: float
    einheit: str
    gemessen_am: datetime = Field(default_factory=datetime.utcnow)
    referenz_min: Optional[float] = None
    referenz_max: Optional[float] = None
    beschreibung: Optional[str] = None

class TransformInput(BaseModel):
    patient: PatientIn
    diagnosen: List[DiagnoseIn] = []
    prozeduren: List[ProzedurIn] = []
    laborwerte: List[LaborwertIn] = []
