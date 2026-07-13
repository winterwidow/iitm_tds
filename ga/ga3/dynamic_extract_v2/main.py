from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import ollama

import json
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExtractRequest(BaseModel):
    document_id: str
    text: str
    schema: dict


@app.post("/")
async def extract(req: ExtractRequest):

    prompt = f"""
You are an information extraction system.

DOCUMENT

{req.text}

JSON SCHEMA

{json.dumps(req.schema, indent=2)}

Rules

Return ONLY valid JSON.

Return JSON that EXACTLY matches the supplied schema.

Do not invent fields.

Missing values must be null.

Dates must be YYYY-MM-DD.

Numbers must be JSON numbers.

Booleans must be JSON booleans.

Return arrays in the same order as they appear in the document.

Do NOT wrap the JSON in markdown.

Do NOT explain anything.
"""

    response = None

    for i in range(3):
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

        except Exception:
            if i == 2:
                raise
            time.sleep(2)

    text = response["message"]["content"].strip()

    # Remove markdown fences if the model still returns them
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    return json.loads(text)
