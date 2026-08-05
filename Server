import os
import uuid
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY", "")

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "service": "Affordplan Sarvam OCR"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/extract", methods=["POST"])
def extract():
    try:
        file = request.files.get("file")
        language = request.form.get("language", "en-IN")
        schema = request.form.get("schema")

        if not file:
            return jsonify({"error": "No file uploaded"}), 400
        if not schema:
            return jsonify({"error": "No schema provided"}), 400
        if not SARVAM_API_KEY:
            return jsonify({"error": "SARVAM_API_KEY not set on server"}), 500

        response = requests.post(
            "https://api.sarvam.ai/doc-ai/v1/job/extract",
            headers={
                "api-subscription-key": SARVAM_API_KEY,
                "Idempotency-Key": str(uuid.uuid4()),
            },
            files={"file": (file.filename, file.stream, file.mimetype)},
            data={
                "language": language,
                "output_format": "json",
                "model": "sarvam-vision-v1",
                "schema": schema,
            },
            timeout=60
        )

        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
