from fastapi import FastAPI, HTTPException, Request, Body
from pydantic import BaseModel
import tempfile
import os
import garak.cli
import json
import hashlib

app = FastAPI()

@app.get('/health')
def health_check():
    return {'status': 'ok'}

@app.post('/scan')
def scan(req: Request):

    args = [
        '--probes', req.probe,
        '--model_name', req.model_type,
        '--model_type', req.model_name,
        # '--detectors', ','.join(req.scanners),
        # '--reporters', 'json',
        # '--output_directory', './garak_output',
        # '--report_prefix', req.probe,
    ]

    # Run Garak via its CLI interface
    garak.cli.main(args)

    report_file = f"./garak_output/{req.probe}_report.json"
    try:
        with open(report_file) as f:
            report = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail='Report not found')

    return {'status': 'completed', 'report': report}


@app.post("/submit")
async def scan(request: Request):
    tmpfile_path = None
    try:
        # Grab raw JSON body
        config_data = await request.json()
        report_file = f"{config_data["reporting"]["report_dir"]}/{config_data["reporting"]["report_prefix"]}.report.jsonl"

        config_json_string = json.dumps(config_data)
        sha256_hash = hashlib.sha256(config_json_string.encode('utf-8')).hexdigest()
        print("Job ID", sha256_hash)

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmpfile:
            json.dump(config_data, tmpfile)
            tmpfile_path = tmpfile.name

        # Run Garak with this config
        garak.cli.main(["--config", tmpfile_path])

        if not os.path.exists(report_file):
            raise HTTPException(status_code=500, detail="Report file not found after Garak scan")
        
        with open(report_file) as f:
            json_array = [json.loads(line) for line in f if line.strip()]



    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Garak scan failed: {str(e)}")
    
    finally:
        # Always clean up
        if tmpfile_path and os.path.exists(tmpfile_path):
            os.unlink(tmpfile_path)

    return {"status": "Scan complete", "job_id": sha256_hash, "config_file": tmpfile_path, "report_file": report_file, "report_json": json_array}
