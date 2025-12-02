import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from loguru import logger
from pydantic import ValidationError

from models import TransformInput 
from fhir_handler import transform_to_fhir_bundle
from database import init_db, save_bundle

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "app.log")

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    lambda msg: print(msg, end=""),
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=log_level
)
logger.add(
    log_file,
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=log_level
)

logger.info("Application starting...")

app = Flask(__name__)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]
if not cors_origins:
    # Default to restrictive CORS if not configured
    cors_origins = ["http://localhost:3000"]
    logger.warning("No CORS_ORIGINS configured, using default: http://localhost:3000")

CORS(
    app,
    origins=cors_origins,
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=True
)

logger.info(f"CORS enabled for origins: {cors_origins}")

@app.get("/api/ping")
def ping():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "ok"}

@app.post("/api/transform")
def transform():
    """Transform medical data to FHIR bundle"""
    logger.info("Transform request received")
    try:
        payload = request.get_json(force=True)
        logger.debug(f"Payload received: {payload}")
        
        # Validate input
        inp = TransformInput.model_validate(payload)
        
        # Transform to FHIR
        bundle = transform_to_fhir_bundle(inp)
        bundle_json = json.loads(bundle.json())
        
        # Save to database
        init_db()
        save_bundle(
            bundle_json["id"], 
            json.dumps(bundle_json), 
            datetime.utcnow().isoformat()
        )
        
        logger.info(f"Successfully created FHIR bundle: {bundle_json['id']}")
        return jsonify(bundle_json), 201
        
    except ValidationError as ve:
        logger.warning(f"Validation error: {ve}")
        return jsonify({
            "error": "Invalid input data",
            "details": ve.errors()
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error during transformation: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path}")
    return jsonify({
        "error": "Not found",
        "message": f"The requested URL {request.path} was not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {error}", exc_info=True)
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

if __name__ == "__main__":
    # Get configuration from environment
    flask_env = os.getenv("FLASK_ENV", "production")
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    # Override debug mode based on environment
    if flask_env == "development" and not os.getenv("FLASK_DEBUG"):
        debug_mode = True
        logger.info("Development environment detected, enabling debug mode")
    
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    
    logger.info(f"Starting Flask app on {host}:{port} (debug={debug_mode}, env={flask_env})")
    app.run(host=host, port=port, debug=debug_mode)
