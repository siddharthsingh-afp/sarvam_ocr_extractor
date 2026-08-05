import os
import uuid
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY", "")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Sarvam OCR Extractor</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; min-height: 100vh; padding: 24px; color: #1a1a1a; }
  h1 { font-size: 18px; font-weight: 600; margin-bottom: 20px; color: #111; }
  .app { display: grid; grid-template-columns: 380px 1fr; gap: 20px; max-width: 1100px; margin: 0 auto; }
  .panel { background: #fff; border: 1px solid #e5e5e5; border-radius: 12px; padding: 20px; }
  .section-label { font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; }
  .section { margin-bottom: 20px; }
  input[type="text"], select { width: 100%; padding: 8px 10px; font-size: 14px; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; color: #1a1a1a; font-family: inherit; outline: none; }
  input:focus, select:focus { border-color: #4f7ef7; box-shadow: 0 0 0 3px rgba(79,126,247,0.1); }
  input::placeholder { color: #bbb; }
  .field-headers { display: grid; grid-template-columns: 1fr 1fr 28px; gap: 6px; margin-bottom: 4px; }
  .field-header-label { font-size: 11px; color: #aaa; }
  .field-row { display: grid; grid-template-columns: 1fr 1fr 28px; gap: 6px; margin-bottom: 8px; align-items: center; }
  .field-row input { padding: 6px 8px; font-size: 13px; }
  .remove-btn { width: 28px; height: 28px; border: 1px solid #ddd; border-radius: 6px; background: none; color: #aaa; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  .remove-btn:hover { background: #fff0f0; border-color: #f99; color: #e55; }
  .add-btn { width: 100%; padding: 8px; font-size: 13px; border: 1px dashed #ccc; border-radius: 8px; background: none; color: #888; cursor: pointer; font-family: inherit; }
  .add-btn:hover { background: #f9f9f9; color: #444; }
  .drop-zone { border: 2px dashed #ddd; border-radius: 12px; padding: 40px 20px; text-align: center; cursor: pointer; transition: all 0.15s; background: #fafafa; margin-bottom: 16px; }
  .drop-zone:hover, .drop-zone.drag-over { border-color: #4f7ef7; background: #f0f4ff; }
  .drop-zone.has-file { border-style: solid; border-color: #22c55e; background: #f0fdf4; }
  .drop-text { font-size: 14px; color: #555; margin-bottom: 4px; }
  .drop-sub { font-size: 12px; color: #aaa; }
  .file-name { font-size: 14px; font-weight: 600; color: #16a34a; }
  .extract-btn { width: 100%; padding: 11px; font-size: 14px; font-weight: 600; border: none; border-radius: 8px; background: #4f7ef7; color: #fff; cursor: pointer; font-family: inherit; display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 20px; }
  .extract-btn:disabled { opacity: 0.45; cursor: not-allowed; }
  .extract-btn:not(:disabled):hover { background: #3b6ae8; }
  .result-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 300px; color: #ccc; font-size: 14px; gap: 10px; }
  .result-box { background: #fafafa; border: 1px solid #e5e5e5; border-radius: 10px; padding: 16px; }
  .result-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
  .result-label { font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.06em; }
  .copy-btn { font-size: 12px; border: 1px solid #ddd; border-radius: 6px; padding: 4px 10px; background: none; color: #666; cursor: pointer; font-family: inherit; }
  .copy-btn:hover { background: #f5f5f5; }
  pre { font-family: 'Courier New', monospace; font-size: 13px; white-space: pre-wrap; line-height: 1.6; max-height: 460px; overflow-y: auto; }
  .error-box { background: #fff5f5; border: 1px solid #fca5a5; border-radius: 10px; padding: 16px; }
  .error-title { font-size: 13px; font-weight: 600; color: #dc2626; margin-bottom: 6px; }
  .error-text { font-size: 13px; color: #b91c1c; line-height: 1.6; }
  .spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.35); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  @media (max-width: 780px) { .app { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<h1>Sarvam OCR Extractor</h1>
<div class="app">
  <div class="panel">
    <div class="section">
      <div class="section-label">Language</div>
      <select id="language">
        <option value="en-IN">English (en-IN)</option>
        <option value="hi-IN">Hindi (hi-IN)</option>
        <option value="bn-IN">Bengali (bn-IN)</option>
        <option value="ta-IN">Tamil (ta-IN)</option>
        <option value="te-IN">Telugu (te-IN)</option>
        <option value="mr-IN">Marathi (mr-IN)</option>
        <option value="gu-IN">Gujarati (gu-IN)</option>
        <option value="kn-IN">Kannada (kn-IN)</option>
        <option value="ml-IN">Malayalam (ml-IN)</option>
      </select>
    </div>
    <div class="section">
      <div class="section-label">Fields to extract</div>
      <div class="field-headers">
        <span class="field-header-label">Field name</span>
        <span class="field-header-label">Description</span>
        <span></span>
      </div>
      <div id="fieldsContainer"></div>
      <button class="add-btn" onclick="addField()">+ Add field</button>
    </div>
  </div>
  <div class="panel">
    <div class="section">
      <div class="section-label">Document</div>
      <div class="drop-zone" id="dropZone"
        onclick="document.getElementById('fileInput').click()"
        ondragover="onDragOver(event)" ondragleave="onDragLeave(event)" ondrop="onDrop(event)">
        <div style="font-size:32px;margin-bottom:10px;" id="dropIcon">📄</div>
        <div class="drop-text" id="dropText">Drop a prescription or click to upload</div>
        <div class="drop-sub" id="dropSub">PDF, PNG, JPG supported</div>
      </div>
      <input type="file" id="fileInput" accept=".pdf,.png,.jpg,.jpeg" style="display:none" onchange="onFileSelect(event)" />
    </div>
    <button class="extract-btn" id="extractBtn" onclick="runExtract()" disabled>
      🔍 Extract fields
    </button>
    <div id="resultArea">
      <div class="result-placeholder">
        <span style="font-size:40px;">🗂️</span>
        <span>Results will appear here</span>
      </div>
    </div>
  </div>
</div>
<script>
  let selectedFile = null;
  let fieldId = 7;
  let fields = [
    { id: 1, name: 'patient_name',   desc: 'Full name of the patient' },
    { id: 2, name: 'patient_age',    desc: 'Age of the patient' },
    { id: 3, name: 'patient_gender', desc: 'Gender of the patient' },
    { id: 4, name: 'patient_phone',  desc: 'Contact number of the patient' },
    { id: 5, name: 'medicines',      desc: 'Medicines with name, strength, frequency, duration' },
    { id: 6, name: 'lab_tests',      desc: 'Lab tests ordered' },
  ];

  function renderFields() {
    document.getElementById('fieldsContainer').innerHTML = fields.map(f => `
      <div class="field-row">
        <input type="text" placeholder="field_name" value="${f.name}" oninput="updateField(${f.id},'name',this.value)" />
        <input type="text" placeholder="what to extract" value="${f.desc}" oninput="updateField(${f.id},'desc',this.value)" />
        <button class="remove-btn" onclick="removeField(${f.id})">×</button>
      </div>`).join('');
  }

  function addField() { fields.push({ id: fieldId++, name: '', desc: '' }); renderFields(); }
  function removeField(id) { fields = fields.filter(f => f.id !== id); renderFields(); }
  function updateField(id, key, value) { const f = fields.find(x => x.id === id); if (f) f[key] = value; }
  function onDragOver(e) { e.preventDefault(); document.getElementById('dropZone').classList.add('drag-over'); }
  function onDragLeave() { document.getElementById('dropZone').classList.remove('drag-over'); }
  function onDrop(e) { e.preventDefault(); document.getElementById('dropZone').classList.remove('drag-over'); const f = e.dataTransfer.files[0]; if (f) setFile(f); }
  function onFileSelect(e) { const f = e.target.files[0]; if (f) setFile(f); }

  function setFile(file) {
    selectedFile = file;
    document.getElementById('dropZone').classList.add('has-file');
    document.getElementById('dropIcon').textContent = '✅';
    document.getElementById('dropText').innerHTML = `<span class="file-name">${file.name}</span>`;
    document.getElementById('dropSub').textContent = (file.size / 1024).toFixed(0) + ' KB — click to change';
    document.getElementById('extractBtn').disabled = false;
  }

  function syntaxColor(json) {
    return json.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/("(\\\\u[a-zA-Z0-9]{4}|\\\\[^u]|[^\\\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g, m => {
        let s = 'color:#4f7ef7';
        if (/^"/.test(m)) s = /:$/.test(m) ? 'color:#1a1a1a;font-weight:600' : 'color:#16a34a';
        else if (/true|false/.test(m)) s = 'color:#d97706';
        else if (/null/.test(m)) s = 'color:#aaa';
        return `<span style="${s}">${m}</span>`;
      });
  }

  let lastResult = null;

  async function runExtract() {
    if (!selectedFile) return;
    const btn = document.getElementById('extractBtn');
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div> Extracting...';
    document.getElementById('resultArea').innerHTML = `<div class="result-placeholder"><div class="spinner" style="width:24px;height:24px;border-color:#ddd;border-top-color:#4f7ef7"></div><span style="font-size:13px;color:#888">Sending to Sarvam...</span></div>`;

    const schema = { type: 'object', properties: {} };
    fields.filter(f => f.name.trim()).forEach(f => {
      schema.properties[f.name.trim()] = { type: 'string', description: f.desc || f.name };
    });

    const form = new FormData();
    form.append('file', selectedFile);
    form.append('language', document.getElementById('language').value);
    form.append('schema', JSON.stringify(schema));

    try {
      const res = await fetch('/extract', { method: 'POST', body: form });
      if (!res.ok) { const t = await res.text(); throw new Error(`${res.status} — ${t}`); }
      const data = await res.json();
      lastResult = data;
      document.getElementById('resultArea').innerHTML = `
        <div class="result-box">
          <div class="result-header">
            <span class="result-label">Extracted data</span>
            <button class="copy-btn" onclick="copyResult()">📋 Copy JSON</button>
          </div>
          <pre>${syntaxColor(JSON.stringify(data, null, 2))}</pre>
        </div>`;
    } catch (err) {
      document.getElementById('resultArea').innerHTML = `
        <div class="error-box">
          <div class="error-title">⚠️ Error</div>
          <div class="error-text">${err.message}</div>
        </div>`;
    } finally {
      btn.disabled = false;
      btn.innerHTML = '🔍 Extract fields';
      if (selectedFile) btn.disabled = false;
    }
  }

  function copyResult() {
    if (lastResult) navigator.clipboard.writeText(JSON.stringify(lastResult, null, 2))
      .then(() => { document.querySelector('.copy-btn').textContent = '✅ Copied'; setTimeout(() => document.querySelector('.copy-btn').textContent = '📋 Copy JSON', 1500); });
  }

  renderFields();
</script>
</body>
</html>"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML)

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
