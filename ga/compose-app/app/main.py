from fastapi import FastAPI
import redis

app = FastAPI()

r = redis.Redis(host="redis", port=6379, decode_responses=True)


@app.get("/healthz")
def health():
    try:
        r.ping()
        return {"status": "ok", "redis": "up"}
    except:
        return {"status": "error", "redis": "down"}


@app.post("/hit/{key}")
def hit(key: str):

    count = r.incr(key)

    return {"key": key, "count": count}


@app.get("/count/{key}")
def count(key: str):

    value = r.get(key)

    if value is None:
        value = 0

    return {"key": key, "count": int(value)}
