from typing import List
from uuid import uuid4
from datetime import datetime
from fhir.resources.bundle import Bundle
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.condition import Condition
from fhir.resources.procedure import Procedure
from fhir.resources.observation import Observation
from fhir.resources.reference import Reference
from fhir.resources.meta import Meta

from models import TransformInput, DiagnoseIn, ProzedurIn, LaborwertIn

SYSTEM_ICD10 = "http://hl7.org/fhir/sid/icd-10"
SYSTEM_OPS   = "http://fhir.de/CodeSystem/dimdi/ops"   # gängig in DE
SYSTEM_LOINC = "http://loinc.org"

def _patient_resource(inp: TransformInput) -> Patient:
    pid = inp.patient.id or f"pat-{uuid4()}"
    name = HumanName(family=inp.patient.nachname, given=[inp.patient.vorname])
    return Patient.construct(
        id=pid,
        resourceType="Patient",
        name=[name],
        gender=inp.patient.geschlecht,
        birthDate=str(inp.patient.geburtsdatum),
        meta=Meta(profile=["http://hl7.org/fhir/StructureDefinition/Patient"])
    )

def _condition_resource(diag: DiagnoseIn, patient_ref: Reference) -> Condition:
    coding = Coding(system=SYSTEM_ICD10, code=diag.icd10, display=diag.beschreibung)
    code = CodeableConcept(coding=[coding], text=diag.beschreibung or diag.icd10)
    return Condition.construct(
        id=f"cond-{uuid4()}",
        resourceType="Condition",
        subject=patient_ref,
        code=code,
        clinicalStatus=CodeableConcept(text=diag.klinischer_status),
        onsetDateTime=str(diag.begonnen_am) if diag.begonnen_am else None
    )

def _procedure_resource(proc: ProzedurIn, patient_ref: Reference) -> Procedure:
    coding = Coding(system=SYSTEM_OPS, code=proc.ops, display=proc.beschreibung)
    code = CodeableConcept(coding=[coding], text=proc.beschreibung or proc.ops)
    return Procedure.construct(
        id=f"proc-{uuid4()}",
        resourceType="Procedure",
        subject=patient_ref,
        code=code,
        performedDateTime=str(proc.datum) if proc.datum else None,
        status="completed"
    )

def _observation_resource(lab: LaborwertIn, patient_ref: Reference) -> Observation:
    coding = Coding(system=SYSTEM_LOINC, code=lab.loinc, display=lab.beschreibung)
    code = CodeableConcept(coding=[coding], text=lab.beschreibung or lab.loinc)

    ref_range = None
    if lab.referenz_min is not None or lab.referenz_max is not None:
        rr = {}
        if lab.referenz_min is not None:
            rr["low"] = {"value": lab.referenz_min, "unit": lab.einheit}
        if lab.referenz_max is not None:
            rr["high"] = {"value": lab.referenz_max, "unit": lab.einheit}
        ref_range = [rr]

    return Observation.construct(
        id=f"obs-{uuid4()}",
        resourceType="Observation",
        status="final",
        category=[CodeableConcept(text="laboratory")],
        code=code,
        subject=patient_ref,
        effectiveDateTime=lab.gemessen_am.isoformat(),
        valueQuantity={"value": lab.wert, "unit": lab.einheit},
        referenceRange=ref_range
    )

def transform_to_fhir_bundle(inp: TransformInput) -> Bundle:
    patient = _patient_resource(inp)
    pref = Reference(reference=f"Patient/{patient.id}")

    resources = [patient]
    resources += [_condition_resource(d, pref) for d in inp.diagnosen]
    resources += [_procedure_resource(p, pref) for p in inp.prozeduren]
    resources += [_observation_resource(l, pref) for l in inp.laborwerte]

    entries = [{"resource": r} for r in resources]

    return Bundle.construct(
        id=f"bundle-{uuid4()}",
        resourceType="Bundle",
        type="collection",
        timestamp=datetime.utcnow().isoformat(),
        entry=entries
    )
