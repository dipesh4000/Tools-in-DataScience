import logging
import random
import time

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI Observability Demo")

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Number of active HTTP requests",
)

@app.middleware("http")
async def observe_requests(request: Request, call_next):
    # Middleware runs before and after every request
    start = time.perf_counter()
    ACTIVE_REQUESTS.inc()

    try:
        response = await call_next(request)
        return response
    finally:
        duration = time.perf_counter() - start

        endpoint = request.url.path
        method = request.method
        status_code = getattr(locals().get("response", None), "status_code", 500)

        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code),
        ).inc()

        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)

        ACTIVE_REQUESTS.dec()

        logger.info(
            "request method=%s endpoint=%s status=%s duration=%.4fs",
            method,
            endpoint,
            status_code,
            duration,
        )

@app.get("/")
def home():
    return {"message": "FastAPI observability demo"}

@app.get("/work")
def work():
    # Simulate variable work
    delay = random.uniform(0.05, 0.5)
    time.sleep(delay)
    return {"delay": delay}

@app.get("/fail")
def fail():
    # Simulate an error
    logger.warning("intentional failure endpoint called")
    return Response("something failed", status_code=500)

@app.get("/metrics")
def metrics():
    # Prometheus scrapes this endpoint
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)