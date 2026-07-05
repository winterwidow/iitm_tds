import time
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

EMAIL = "24f2004692@ds.study.iitm.ac.in"

app = FastAPI()

START_TIME = time.time()

# Prometheus counter
REQUEST_COUNTER = Counter("http_requests_total", "Total HTTP requests")

# Keep last 100 log entries
logs = deque(maxlen=100)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    REQUEST_COUNTER.inc()

    logs.append(
        {
            "level": "INFO",
            "ts": time.time(),
            "path": request.url.path,
            "request_id": str(time.time_ns()),
        }
    )

    response = await call_next(request)
    return response


@app.get("/work")
def work(n: int):

    # simulate work
    for _ in range(n * 1000):
        pass

    return {"email": EMAIL, "done": n}


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/healthz")
def health():

    return {"status": "ok", "uptime_s": time.time() - START_TIME}


@app.get("/logs/tail")
def tail(n: int = 10):

    return list(logs)[-n:]
