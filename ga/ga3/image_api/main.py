from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import base64

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ImageRequest(BaseModel):
    image_base64: str
    question: str


@app.post("/answer-image")
async def answer_image(req: ImageRequest):

    prompt = f"""
You are an OCR and document understanding assistant.

Carefully read the image and answer the user's question.

Question:
{req.question}

Rules:
- Return ONLY the answer.
- No explanation.
- If the answer is numeric:
    * Return only the number.
    * No commas.
    * No currency symbols.
    * No units.
- If the answer is text:
    * Return only the exact text.
"""

    response = client.models.generate_content(
        model="gemini-3-pro-image",
        contents=[
            types.Part.from_bytes(
                data=base64.b64decode(req.image_base64),
                mime_type="image/png",
            ),
            prompt,
        ],
        config=types.GenerateContentConfig(
            temperature=0,
        ),
    )

    return {"answer": response.text.strip()}
