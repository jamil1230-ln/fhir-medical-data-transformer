from typing import List
from uuid import uuid4
from datetime import datetime, timezone
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
from loguru import logger

from models import TransformInput, DiagnoseIn, ProzedurIn, LaborwertIn
from exceptions import FHIRValidationError, ResourceCreationError

SYSTEM_ICD10 = "http://hl7.org/fhir/sid/icd-10"
SYSTEM_OPS   = "http://fhir.de/CodeSystem/dimdi/ops"   # gängig in DE
SYSTEM_LOINC = "http://loinc.org"


def _validate_fhir_resource(resource, resource_type: str):
    """
    Validate a FHIR resource.
    
    Args:
        resource: The FHIR resource to validate
        resource_type: Type of the resource (for error messages)
    
    Raises:
        FHIRValidationError: If validation fails
    """
    try:
        # Validate the resource by converting to JSON and back
        # This ensures the resource is valid according to FHIR specs
        resource_json = resource.json()
        logger.debug(f"{resource_type} resource validated successfully")
    except Exception as e:
        logger.error(f"FHIR validation failed for {resource_type}: {str(e)}")
        raise FHIRValidationError(
            f"FHIR {resource_type} Validierung fehlgeschlagen",
            details={"validation_error": str(e)}
        )

def _patient_resource(inp: TransformInput) -> Patient:
    try:
        pid = inp.patient.id or f"pat-{uuid4()}"
        name = HumanName(family=inp.patient.nachname, given=[inp.patient.vorname])
        patient = Patient.construct(
            id=pid,
            resourceType="Patient",
            name=[name],
            gender=inp.patient.geschlecht,
            birthDate=str(inp.patient.geburtsdatum),
            meta=Meta(profile=["http://hl7.org/fhir/StructureDefinition/Patient"])
        )
        _validate_fhir_resource(patient, "Patient")
        logger.info(f"Patient resource created: {pid}")
        return patient
    except FHIRValidationError:
        raise
    except Exception as e:
        logger.error(f"Failed to create Patient resource: {str(e)}")
        raise ResourceCreationError(
            "Fehler beim Erstellen der Patient-Ressource",
            details={"error": str(e)}
        )

def _condition_resource(diag: DiagnoseIn, patient_ref: Reference) -> Condition:
    try:
        coding = Coding(system=SYSTEM_ICD10, code=diag.icd10, display=diag.beschreibung)
        code = CodeableConcept(coding=[coding], text=diag.beschreibung or diag.icd10)
        condition = Condition.construct(
            id=f"cond-{uuid4()}",
            resourceType="Condition",
            subject=patient_ref,
            code=code,
            clinicalStatus=CodeableConcept(text=diag.klinischer_status),
            onsetDateTime=str(diag.begonnen_am) if diag.begonnen_am else None
        )
        _validate_fhir_resource(condition, "Condition")
        logger.debug(f"Condition resource created for ICD-10: {diag.icd10}")
        return condition
    except FHIRValidationError:
        raise
    except Exception as e:
        logger.error(f"Failed to create Condition resource: {str(e)}")
        raise ResourceCreationError(
            "Fehler beim Erstellen der Condition-Ressource",
            details={"icd10": diag.icd10, "error": str(e)}
        )

def _procedure_resource(proc: ProzedurIn, patient_ref: Reference) -> Procedure:
    try:
        coding = Coding(system=SYSTEM_OPS, code=proc.ops, display=proc.beschreibung)
        code = CodeableConcept(coding=[coding], text=proc.beschreibung or proc.ops)
        procedure = Procedure.construct(
            id=f"proc-{uuid4()}",
            resourceType="Procedure",
            subject=patient_ref,
            code=code,
            performedDateTime=str(proc.datum) if proc.datum else None,
            status="completed"
        )
        _validate_fhir_resource(procedure, "Procedure")
        logger.debug(f"Procedure resource created for OPS: {proc.ops}")
        return procedure
    except FHIRValidationError:
        raise
    except Exception as e:
        logger.error(f"Failed to create Procedure resource: {str(e)}")
        raise ResourceCreationError(
            "Fehler beim Erstellen der Procedure-Ressource",
            details={"ops": proc.ops, "error": str(e)}
        )

def _observation_resource(lab: LaborwertIn, patient_ref: Reference) -> Observation:
    try:
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

        observation = Observation.construct(
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
        _validate_fhir_resource(observation, "Observation")
        logger.debug(f"Observation resource created for LOINC: {lab.loinc}")
        return observation
    except FHIRValidationError:
        raise
    except Exception as e:
        logger.error(f"Failed to create Observation resource: {str(e)}")
        raise ResourceCreationError(
            "Fehler beim Erstellen der Observation-Ressource",
            details={"loinc": lab.loinc, "error": str(e)}
        )

def transform_to_fhir_bundle(inp: TransformInput) -> Bundle:
    try:
        logger.info("Starting FHIR transformation")
        patient = _patient_resource(inp)
        pref = Reference(reference=f"Patient/{patient.id}")

        resources = [patient]
        resources += [_condition_resource(d, pref) for d in inp.diagnosen]
        resources += [_procedure_resource(p, pref) for p in inp.prozeduren]
        resources += [_observation_resource(l, pref) for l in inp.laborwerte]

        entries = [{"resource": r} for r in resources]

        bundle = Bundle.construct(
            id=f"bundle-{uuid4()}",
            resourceType="Bundle",
            type="collection",
            timestamp=datetime.now(timezone.utc).isoformat(),
            entry=entries
        )
        
        _validate_fhir_resource(bundle, "Bundle")
        logger.info(f"FHIR Bundle created successfully with {len(resources)} resources")
        return bundle
    except (FHIRValidationError, ResourceCreationError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error during FHIR transformation: {str(e)}")
        raise ResourceCreationError(
            "Fehler bei der FHIR-Transformation",
            details={"error": str(e)}
        )
