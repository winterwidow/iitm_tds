from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
import json

app = FastAPI()


class Request(BaseModel):
    text: str


class Response(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


SYSTEM_PROMPT = """
You extract invoice information.

Return ONLY valid JSON.

Schema:
{
  "vendor": string,
  "amount": number,
  "currency": string,
  "date": string
}

Rules:
- vendor is the invoice vendor/company.
- amount is the total amount due as a number.
- currency must be the 3-letter ISO currency code in uppercase (USD, EUR, GBP, INR, etc.).
- Convert currency symbols ($, €, £, ₹) into ISO codes.
- date must be in YYYY-MM-DD format.
- If a field cannot be determined, return:
    vendor=""
    amount=0
    currency=""
    date=""
Return ONLY valid JSON.
"""


@app.post("/extract", response_model=Response)
def extract(req: Request):

    # Empty input -> 422
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="Input text cannot be empty")

    try:

        response = ollama.chat(
            model="gemma3:latest",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": req.text,
                },
            ],
            format="json",
        )

        data = json.loads(response["message"]["content"])

        # Make sure every field exists
        return {
            "vendor": str(data.get("vendor", "")),
            "amount": float(data.get("amount", 0)),
            "currency": str(data.get("currency", "")).upper(),
            "date": str(data.get("date", "")),
        }

    except HTTPException:
        raise

    except Exception:
        # Never return HTTP 500
        raise HTTPException(status_code=422, detail="Unable to extract invoice fields")
