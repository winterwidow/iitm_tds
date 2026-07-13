from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import ollama

import json
import time
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExtractRequest(BaseModel):
    text: str
    schema: dict


def clean_string(value):
    if value is None:
        return None

    value = str(value)

    # normalize whitespace
    value = re.sub(r"\s+", " ", value).strip()

    # remove surrounding quotes
    value = value.strip("\"'")

    # remove trailing punctuation
    value = re.sub(r"[.,;:]+$", "", value)

    return value


@app.post("/dynamic-extract")
async def dynamic_extract(req: ExtractRequest):

    schema_json = json.dumps(req.schema, indent=2)

    prompt = f"""
You are an information extraction system.

Extract information from the text below.

TEXT

{req.text}

SCHEMA

{schema_json}

Rules:

- Return ONLY valid JSON.
- Return EXACTLY the keys in the schema.
- Do NOT invent extra keys.
- Missing values must be null.
- string -> JSON string
- integer -> JSON integer
- float -> JSON number
- boolean -> true or false
- date -> YYYY-MM-DD
- Do NOT explain anything.
- Do NOT wrap the JSON in markdown.
"""

    response = None

    for attempt in range(3):
        try:

            response = ollama.chat(
                model="gemma3:latest",
                format="json",
                options={
                    "temperature": 0,
                },
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            break

        except Exception as e:

            if attempt == 2:
                raise e

            time.sleep(2)

    text = response["message"]["content"].strip()

    # Remove markdown if the model still returns it
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    print(text)

    data = json.loads(text)

    result = {}

    for key, typ in req.schema.items():

        value = data.get(key)

        if value is None:
            result[key] = None
            continue

        try:

            if typ == "string":
                result[key] = clean_string(value)

            elif typ == "integer":
                result[key] = int(value)

            elif typ == "float":
                result[key] = float(value)

            elif typ == "boolean":

                if isinstance(value, bool):
                    result[key] = value

                elif isinstance(value, str):
                    result[key] = value.lower() == "true"

                else:
                    result[key] = bool(value)

            elif typ == "date":
                result[key] = clean_string(value)

            else:
                result[key] = value

        except Exception:
            result[key] = None

    return result
