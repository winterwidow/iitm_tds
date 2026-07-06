import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

EMAIL = "24f2004692@ds.study.iitm.ac.in"

ALLOWED_ORIGIN = "https://dash-0x6i6q.example.com"

app = FastAPI()

# --------------------
# CORS
# --------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Middleware
# --------------------


class MetricsMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start

        response.headers["X-Request-ID"] = str(uuid.uuid4())
        response.headers["X-Process-Time"] = f"{duration:.6f}"

        return response


app.add_middleware(MetricsMiddleware)

# --------------------
# Endpoint
# --------------------


@app.get("/stats")
def stats(values: str):

    try:
        nums = [int(x) for x in values.split(",")]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid integers")

    if len(nums) == 0:
        raise HTTPException(status_code=400, detail="No values")

    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
    }
