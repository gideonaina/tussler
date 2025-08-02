import asyncio
import websockets

CONFIG = """
{
  "system": {
    "verbose": 0,
    "parallel_requests": true
  },
  "run": {
    "generations": 1,
    "deprefix": true
  },
  "plugins": {
    "model_type": "rest",
    "probe_spec": "encoding",
    "generators": {
      "rest": {
        "RestGenerator": {
          "uri": "http://ollama:11434/api/generate",
          "method": "post",
          "headers": {
            "Content-Type": "application/json",
            "X-Authorization": "Bearer test_token"
          },
          "req_template_json_object": {
            "model": "llama3",
            "messages": [
              {
                "role": "user",
                "content": "$INPUT"
              }
            ]
          },
          "response_json": true,
          "response_json_field": "response",
          "request_timeout": 3600
        }
      }
    }
  },
  "reporting": {
    "report_dir": "/tmp/garak_output",
    "report_prefix": "ollama3_run"
  },
  "metadata":{
    "client": {
        "poc": "john.doe",
        "email": "john.doe@example.com"
    },
    "engagement": {
        "id": "tussler-ollama3",
        "name": "Tussler Ollama3 Test",
        "description": "Testing Tussler with Ollama3 model with Garak test engine",
        "tags": ["tussler", "ollama3", "test"],
        "version": "1.0.0",
        "created_at": "2023-10-01T00:00:00Z",
        "updated_at": "2023-10-01T00:00:00Z",
        "created_by": "gideon.aina"
    },
    "engine": "garak"
  }
}
"""

    # async with websockets.connect(
    #     "ws://localhost:8081/ws/v1/submit",
    #     ping_interval=10,  # seconds between pings
    #     ping_timeout=90    # seconds to wait for pong
    # ) as ws:

async def send_initial_payload():
    uri = "ws://localhost:8081/ws/v1/submit"
    async with websockets.connect(
        uri,
        ping_interval=10,  # seconds between pings
        ping_timeout=250000    # seconds to wait for pong
    ) as ws:

        await ws.send(CONFIG)

        # Receive and print responses
        while True:
            try:
                msg = await ws.recv()
                print(f"{msg}")
            except websockets.exceptions.ConnectionClosed:
                break

if __name__ == "__main__":
    asyncio.run(send_initial_payload())
