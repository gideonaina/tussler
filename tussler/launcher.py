from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from garak._config import load_base_config, load_config
import garak.cli
import json

class ScanRequest(BaseModel):
    probe: str
    scanners: list[str] = ['prompt_injection']

app = FastAPI()

@app.get('/health')
def health_check():
    return {'status': 'ok'}

@app.post('/scan')
def scan(req: ScanRequest = Body(...)):
    # # Load Garak base and site config
    # load_base_config()
    # cfg = load_config()

    # # Set the probe and detectors (scanners) for this run
    # cfg.probes = [req.probe]
    # cfg.detectors = req.scanners     # 'scanners' → detectors
    # cfg.reporters = ['json']
    # cfg.output_directory = './garak_output'

    # # Build CLI arguments for garak
    # args = [
    #     '--probes', req.probe,
    #     '--detectors', ','.join(req.scanners),
    #     '--report_prefix', req.probe,
    #     # '--config', str(cfg)  # (optional: if using a config file or config object)
    # ]

    args = [
        '--probes', req.probe,
        '--detectors', ','.join(req.scanners),
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
