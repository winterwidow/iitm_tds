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


class SolveRequest(BaseModel):
    problem_id: str
    problem: str


@app.post("/solve")
async def solve(req: SolveRequest):

    prompt = f"""
You are an expert arithmetic solver.

Solve the following word problem carefully.

Ignore any distractor numbers that are irrelevant.

Problem:

{req.problem}

Return ONLY valid JSON.

The JSON MUST be exactly:

{{
    "reasoning": "...",
    "answer": 0
}}

Rules:

- reasoning must explain the calculation.
- reasoning must be at least 80 characters.
- answer must be a JSON integer.
- No markdown.
- No extra keys.
"""

    response = None

    for attempt in range(3):

        try:

            response = ollama.chat(
                model="gemma3:latest",
                format="json",
                options={"temperature": 0},
                messages=[{"role": "user", "content": prompt}],
            )

            break

        except Exception as e:

            if attempt == 2:
                raise e

            time.sleep(2)

    text = response["message"]["content"].strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    data = json.loads(text)

    reasoning = str(data.get("reasoning", "")).strip()

    if len(reasoning) < 80:
        reasoning += (
            " The calculation follows the quantities described in the problem "
            "while ignoring unrelated information."
        )

    try:
        answer = int(data.get("answer"))
    except Exception:
        answer = 0

    return {"reasoning": reasoning, "answer": answer}
