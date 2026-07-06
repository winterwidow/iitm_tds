from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import time

EMAIL = "24f2004692@ds.study.iitm.ac.in"

ALLOWED_ORIGINS = {
    "https://app-ubklge.example.com",
    "https://exam.sanand.workers.dev",
}

RATE_LIMIT = 12
WINDOW = 10

app = FastAPI()

client_buckets = {}


# -------------------------------------------------------
# Middleware 1: Request Context
# -------------------------------------------------------


class RequestContextMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        if request.method == "OPTIONS":
            return await call_next(request)

        request_id = request.headers.get("X-Request-ID")

        if not request_id:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        return response


# -------------------------------------------------------
# Middleware 2: Rate Limiter
# -------------------------------------------------------


class RateLimitMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        if request.method == "OPTIONS":
            return await call_next(request)

        client = request.headers.get("X-Client-Id")

        if client:

            now = time.monotonic()

            timestamps = client_buckets.get(client, [])

            timestamps = [t for t in timestamps if now - t < WINDOW]

            if len(timestamps) >= RATE_LIMIT:
                return JSONResponse(
                    status_code=429, content={"detail": "Rate limit exceeded"}
                )

            timestamps.append(now)

            client_buckets[client] = timestamps

        return await call_next(request)


# -------------------------------------------------------
# Middleware 3: Manual CORS
# -------------------------------------------------------


class CORSMiddlewareManual(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        origin = request.headers.get("Origin")

        # Preflight
        if request.method == "OPTIONS":

            response = Response(status_code=200)

        else:

            response = await call_next(request)

        if origin in ALLOWED_ORIGINS:

            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"

            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"

            response.headers["Access-Control-Allow-Headers"] = (
                "X-Client-Id, X-Request-ID, Content-Type"
            )

            response.headers["Access-Control-Expose-Headers"] = "X-Request-ID"

        return response


app.add_middleware(RequestContextMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CORSMiddlewareManual)


@app.get("/ping")
async def ping(request: Request):

    return {
        "email": EMAIL,
        "request_id": request.state.request_id,
    }
