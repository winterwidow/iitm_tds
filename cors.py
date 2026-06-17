"""
CORS and Middleware:
CORS (Cross-Origin Resource Sharing) is the browser’s security policy that blocks your React frontend from calling your Python API unless the API explicitly says “it’s okay”. Middleware is code that runs on every request before it hits your route handler — perfect for logging, rate limiting, auth checks, and timing.
"""

# Setting up CORS:

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "https://myapp.vercel.app",  # Production frontend
    ],
    allow_credentials=True,  # Allow cookies / Authorization headers
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Content-Type, Authorization, etc.
)
"""Never use allow_origins=["*"] in production !> ["*"] means any website can call your API. Fine for development, dangerous in production — an attacker’s site could call your API using your users’ cookies."""

# CORS for Public APIs:

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],  # Read-only public API
    allow_headers=["*"],
)

# Custom Middleware Example:

# 1. Request Timing Middleware

import time
from fastapi import Request


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)  # ← run the actual route
    duration = time.time() - start
    response.headers["X-Process-Time"] = str(round(duration * 1000, 2)) + "ms"
    return response

"""Every response now has an X-Process-Time: 23.4ms header. Great for debugging slow endpoints."""
