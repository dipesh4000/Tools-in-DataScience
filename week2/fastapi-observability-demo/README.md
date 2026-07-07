# FastAPI demo (week2/fastapi)

Purpose
- Minimal prediction API demonstrating validation (pydantic), in-memory/redis caching, background logging, and job status.

Run locally
1. Ensure Redis is running on localhost:6379
2. python -m pip install -r requirements.txt
3. uvicorn main:app --reload --port 8000

Endpoints
- GET /health — api + redis status
- POST /predict — body { "text": "some text", "language": "en" } returns prediction
- GET /predict/{id} — retrieve prediction
- PATCH /predict/{id}/feedback — add feedback

Notes
- The current model is a fake_model() heuristic in main.py; replace with your model integration.
- api-events.log will be created in the service working directory for background logs.
