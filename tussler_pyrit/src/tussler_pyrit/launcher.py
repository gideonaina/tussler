import json
import logging

from fastapi import FastAPI, Request, WebSocket

logger = logging.getLogger("uvicorn")

app = FastAPI()

@app.get('/pyrit/health')
def health_check():
    return {'status': 'ok'}


@app.post("/pyrit/api/v1/submit")
async def scan(request: Request):
    return {"job_status": "testing"}


@app.websocket("/pyrit/ws/v1/submit")
async def run_garak_ws(websocket: WebSocket):
    await websocket.send_text(json.dumps({
        "job_id": "testing",
        "type": "websocket"
    }))

