from collections import defaultdict

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

EMAIL = "24f2004692@ds.study.iitm.ac.in"
API_KEY = "ak_lfp5cn3qggn2qbqhzz9gq7gw"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: list[Event]


@app.post("/analytics")
def analytics(
    request: AnalyticsRequest,
    x_api_key: str | None = Header(default=None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    revenue = 0.0
    totals = defaultdict(float)

    for event in request.events:
        if event.amount > 0:
            revenue += event.amount
            totals[event.user] += event.amount

    top_user = max(totals, key=totals.get) if totals else ""

    return {
        "email": EMAIL,
        "total_events": len(request.events),
        "unique_users": len({e.user for e in request.events}),
        "revenue": revenue,
        "top_user": top_user,
    }
