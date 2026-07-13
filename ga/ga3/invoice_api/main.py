from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import json

app = FastAPI()


SYSTEM_PROMPT = """
You extract structured information from invoices.

Return ONLY valid JSON.

Schema:

{
  "invoice_no": string|null,
  "date": string|null,
  "vendor": string|null,
  "amount": number|null,
  "tax": number|null,
  "currency": string|null
}

Rules:

- amount = subtotal BEFORE tax.
- tax = ONLY the tax amount.
- date MUST be YYYY-MM-DD.
- currency should be ISO code like INR, USD, EUR.
- If a field cannot be found return null.
- Return ONLY JSON.
"""


class InvoiceRequest(BaseModel):
    invoice_text: str


@app.post("/extract")
async def extract(req: InvoiceRequest):

    response = ollama.chat(
        model="gemma3:latest",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": req.invoice_text,
            },
        ],
        format="json",
    )

    try:
        data = json.loads(response["message"]["content"])
    except Exception:
        data = {}

    result = {
        "invoice_no": data.get("invoice_no"),
        "date": data.get("date"),
        "vendor": data.get("vendor"),
        "amount": data.get("amount"),
        "tax": data.get("tax"),
        "currency": data.get("currency"),
    }

    return result
