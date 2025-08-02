from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketException, WebSocketDisconnect
from pydantic import BaseModel
import tempfile
import os
import garak.cli
import json
import hashlib
import asyncio
import subprocess
import logging
import contextlib

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
logger = logging.getLogger("uvicorn")

app = FastAPI()

@app.get('/health')
def health_check():
    return {'status': 'ok'}

@app.post('/api/v1/scan')
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


@app.post("/api/v1/submit")
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

    return {"job_status": "complete", "job_id": sha256_hash, "config_file": tmpfile_path, "report_file": report_file, "report_json": json_array}


@app.websocket("/ws/v1/submit")
async def run_garak_ws(websocket: WebSocket):
    
    try:
        await websocket.accept()
        tmpfile_path = None
        logger.info("WebSocket connection established")

        request_data = await websocket.receive_text()
        config_data = json.loads(request_data)

        report_file = f"{config_data["reporting"]["report_dir"]}/{config_data["reporting"]["report_prefix"]}.report.jsonl"

        config_json_string = json.dumps(config_data)
        sha256_hash = hashlib.sha256(config_json_string.encode('utf-8')).hexdigest()
        logger.info("Job ID: %s", sha256_hash)

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmpfile:
            json.dump(config_data, tmpfile)
            tmpfile_path = tmpfile.name

        async def keep_alive():
            try:
                while True:
                    await websocket.send_text("__keepalive__")
                    await asyncio.sleep(2)
            except (asyncio.exceptions.CancelledError, WebSocketDisconnect, WebSocketException):
                logger.info(" Connection closed in Keep alive bolck: %s", e)

        keep_alive_task = asyncio.create_task(keep_alive())
        logger.info("Keep alive task started")

        process = subprocess.Popen(
            ["garak", "--config", tmpfile_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        logger.info("Garak process started with PID: %s", process.pid)

        for line in process.stdout:
            await websocket.send_text(line.rstrip())
        # process.stdout.close()
        # process.wait()

        # try:
        #     keep_alive_task.cancel()
        #     await keep_alive_task
        # except Exception:
        #     pass
        logger.info("Garak process completed")

        with open(report_file) as f:
            report_json = [json.loads(line) for line in f if line.strip()]

        logger.info("Report file read successfully")

        await websocket.send_text(json.dumps({
            "job_id": sha256_hash,
            "status": "complete",
            "config_data": config_data,
            "report": report_json
        }))

        # keep_alive_task.cancel()
        # with contextlib.suppress(asyncio.CancelledError):
        #     await keep_alive_task

        # await websocket.close()

    except WebSocketException as e:
        logger.error("❌ Error:WebSocketException - %s", e)
    except Exception as e:
        await websocket.send_text(f"❌ Error: {e}")
    finally:
        logger.info("Cleaning up resources")
        if tmpfile_path and os.path.exists(tmpfile_path):
            os.unlink(tmpfile_path)
        try:
            process.stdout.close()
            process.wait()
            
            keep_alive_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await keep_alive_task

            await websocket.close()
        except (WebSocketDisconnect, RuntimeError):
            logger.error("❌ Error: %s", e)
        except Exception as e:
            logger.error("❌ Error: %s", e)

