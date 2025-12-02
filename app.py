from flask import Flask, request, jsonify
from models import TransformInput 
from fhir_handler import transform_to_fhir_bundle
from database import init_db, save_bundle
from datetime import datetime
from pydantic import ValidationError
from loguru import logger
import json
import sys

from exceptions import (
    FHIRTransformerError,
    InvalidInputError,
    FHIRValidationError,
    ResourceCreationError,
    DatabaseError
)

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="10 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

app = Flask(__name__)


# Error response standard format
def create_error_response(error_type: str, message: str, details: dict = None, status_code: int = 400):
    """
    Create a standardized error response.
    
    Args:
        error_type: Type of error (e.g., "ValidationError", "FHIRError")
        message: Human-readable error message
        details: Optional dictionary with additional error details
        status_code: HTTP status code
    
    Returns:
        Tuple of (response dict, status code)
    """
    response = {
        "error": error_type,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    if details:
        response["details"] = details
    
    return jsonify(response), status_code


# Custom error handlers
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {str(e)}")
    errors = []
    for error in e.errors():
        field = " -> ".join(str(loc) for loc in error['loc'])
        errors.append({
            "field": field,
            "message": error['msg'],
            "type": error['type']
        })
    
    return create_error_response(
        error_type="ValidationError",
        message="Eingabedaten sind ungültig",
        details={"validation_errors": errors},
        status_code=422
    )


@app.errorhandler(InvalidInputError)
def handle_invalid_input_error(e):
    """Handle custom invalid input errors."""
    logger.warning(f"Invalid input: {e.message}")
    return create_error_response(
        error_type=e.__class__.__name__,
        message=e.message,
        details=e.details,
        status_code=422
    )


@app.errorhandler(FHIRValidationError)
def handle_fhir_validation_error(e):
    """Handle FHIR validation errors."""
    logger.error(f"FHIR validation error: {e.message}")
    return create_error_response(
        error_type=e.__class__.__name__,
        message=e.message,
        details=e.details,
        status_code=422
    )


@app.errorhandler(ResourceCreationError)
def handle_resource_creation_error(e):
    """Handle FHIR resource creation errors."""
    logger.error(f"Resource creation error: {e.message}")
    return create_error_response(
        error_type=e.__class__.__name__,
        message=e.message,
        details=e.details,
        status_code=500
    )


@app.errorhandler(DatabaseError)
def handle_database_error(e):
    """Handle database errors."""
    logger.error(f"Database error: {e.message}")
    return create_error_response(
        error_type=e.__class__.__name__,
        message=e.message,
        details=e.details,
        status_code=500
    )


@app.errorhandler(FHIRTransformerError)
def handle_fhir_transformer_error(e):
    """Handle generic FHIR transformer errors."""
    logger.error(f"FHIR transformer error: {e.message}")
    return create_error_response(
        error_type=e.__class__.__name__,
        message=e.message,
        details=e.details,
        status_code=500
    )


@app.errorhandler(Exception)
def handle_generic_error(e):
    """Handle any uncaught exceptions."""
    logger.exception(f"Unexpected error: {str(e)}")
    return create_error_response(
        error_type="InternalServerError",
        message="Ein unerwarteter Fehler ist aufgetreten",
        details={"error": str(e)},
        status_code=500
    )


@app.get("/api/ping")
def ping():
    logger.debug("Ping endpoint called")
    return {"status": "ok"}


@app.post("/api/transform")
def transform():
    logger.info("Transform endpoint called")
    
    # Validate JSON payload exists
    if not request.is_json:
        logger.warning("Request is not JSON")
        return create_error_response(
            error_type="InvalidContentType",
            message="Content-Type muss 'application/json' sein",
            status_code=400
        )
    
    payload = request.get_json(force=True)
    logger.debug(f"Received payload with keys: {list(payload.keys())}")
    
    # Validate and transform input
    inp = TransformInput.model_validate(payload)
    logger.info(f"Input validated for patient: {inp.patient.vorname} {inp.patient.nachname}")
    
    # Transform to FHIR bundle
    bundle = transform_to_fhir_bundle(inp)
    bundle_json = json.loads(bundle.json())
    
    # Save to database
    init_db()
    save_bundle(bundle_json["id"], json.dumps(bundle_json), datetime.utcnow().isoformat())
    
    logger.info(f"Transformation completed successfully, bundle ID: {bundle_json['id']}")
    return jsonify(bundle_json), 201

if __name__ == "__main__":
    app.run(debug=True)
