import os
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (allow browser-based grader)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()


DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(v):
    return str(v).lower() in ("true", "1", "yes", "on")


@app.get("/effective-config")
def effective_config(request: Request):

    config = DEFAULTS.copy()

    # --------------------
    # YAML
    # --------------------
    with open("config.development.yaml") as f:
        config.update(yaml.safe_load(f))

    # --------------------
    # .env
    # --------------------
    if os.getenv("NUM_WORKERS"):
        config["workers"] = int(os.getenv("NUM_WORKERS"))

    if os.getenv("APP_DEBUG"):
        config["debug"] = to_bool(os.getenv("APP_DEBUG"))

    if os.getenv("APP_API_KEY"):
        config["api_key"] = os.getenv("APP_API_KEY")

    # --------------------
    # OS env (APP_*)
    # --------------------
    env_map = {
        "APP_PORT": ("port", int),
        "APP_DEBUG": ("debug", to_bool),
        "APP_API_KEY": ("api_key", str),
        "APP_WORKERS": ("workers", int),
        "APP_LOG_LEVEL": ("log_level", str),
    }

    for env_name, (key, converter) in env_map.items():
        if env_name in os.environ:
            config[key] = converter(os.environ[env_name])

    # --------------------
    # CLI overrides
    # --------------------
    for item in request.query_params.getlist("set"):
        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key == "port":
            config["port"] = int(value)
        elif key == "workers":
            config["workers"] = int(value)
        elif key == "debug":
            config["debug"] = to_bool(value)
        elif key == "log_level":
            config["log_level"] = value
        elif key == "api_key":
            config["api_key"] = value

    # mask secret
    config["api_key"] = "*****"

    return config