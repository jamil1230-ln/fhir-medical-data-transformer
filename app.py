from flask import Flask, request, jsonify
from models import TransformInput
from fhir_handler import transform_to_fhir_bundle
from database import init_db, save_bundle
from datetime import datetime
import json

app = Flask(__name__)

@app.get("/api/ping")
def ping():
    return {"status": "ok"}

@app.post("/api/transform")
def transform():
    try:
        payload = request.get_json(force=True)
        inp = TransformInput.model_validate(payload)
        bundle = transform_to_fhir_bundle(inp)
        bundle_json = json.loads(bundle.json())
        # optional speichern
        init_db()
        save_bundle(bundle_json["id"], json.dumps(bundle_json), datetime.utcnow().isoformat())
        return jsonify(bundle_json), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
