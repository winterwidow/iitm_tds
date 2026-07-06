from fastapi import FastAPI, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import time
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Retry-After"],
)

TOTAL_ORDERS = 44
RATE_LIMIT = 19
WINDOW = 10

idempotency_store = {}
client_requests = {}


class Order(BaseModel):
    item: str = "item"


# -------------------------
# Cursor helpers
# -------------------------


def encode_cursor(n: int) -> str:
    return base64.urlsafe_b64encode(str(n).encode()).decode()


def decode_cursor(cursor: str) -> int:
    return int(base64.urlsafe_b64decode(cursor.encode()).decode())


# -------------------------
# Rate limiting
# -------------------------


def rate_limit_response(client_id: str):

    now = time.monotonic()

    timestamps = client_requests.get(client_id, [])

    timestamps = [t for t in timestamps if now - t < WINDOW]

    client_requests[client_id] = timestamps

    if len(timestamps) >= RATE_LIMIT:

        retry_after = max(1, int(WINDOW - (now - timestamps[0])) + 1)

        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={"Retry-After": str(retry_after)},
        )

    timestamps.append(now)

    client_requests[client_id] = timestamps

    return None


# -------------------------
# POST /orders
# -------------------------


@app.post("/orders", status_code=201)
def create_order(
    order: Order,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_client_id: str = Header(..., alias="X-Client-Id"),
):

    limited = rate_limit_response(x_client_id)

    if limited:
        return limited

    if idempotency_key in idempotency_store:

        return JSONResponse(status_code=201, content=idempotency_store[idempotency_key])

    created = {
        "id": str(uuid.uuid4()),
        "item": order.item,
    }

    idempotency_store[idempotency_key] = created

    return JSONResponse(
        status_code=201,
        content=created,
    )


# -------------------------
# GET /orders
# -------------------------


@app.get("/orders")
def list_orders(
    limit: int = 10,
    cursor: Optional[str] = None,
    x_client_id: str = Header(..., alias="X-Client-Id"),
):

    limited = rate_limit_response(x_client_id)

    if limited:
        return limited

    if limit < 1:
        limit = 1

    if cursor:
        start = decode_cursor(cursor)
    else:
        start = 1

    end = min(start + limit - 1, TOTAL_ORDERS)

    items = [{"id": i} for i in range(start, end + 1)]

    next_cursor = None

    if end < TOTAL_ORDERS:
        next_cursor = encode_cursor(end + 1)

    return {
        "items": items,
        "next_cursor": next_cursor,
    }


@app.get("/")
def health():
    return {"status": "ok"}
