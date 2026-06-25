from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SentimentRequest(BaseModel):
    sentences: list[str]


def predict_sentiment(text: str):

    text = text.lower()

    happy_keywords = [
        "love",
        "great",
        "awesome",
        "good",
        "happy",
        "excellent",
        "fantastic",
        "amazing",
        "nice",
        "wonderful",
        "best",
        "like",
        "liked",
        "enjoy",
        "perfect",
        "positive",
        "cool",
        "super",
        "fun",
        "brilliant",
        "delight",
        "excited",
        "beautiful",
        "success",
        "successful",
    ]

    sad_keywords = [
        "bad",
        "terrible",
        "sad",
        "awful",
        "hate",
        "worst",
        "horrible",
        "angry",
        "poor",
        "boring",
        "annoying",
        "upset",
        "negative",
        "problem",
        "issue",
        "issues",
        "disappointed",
        "pain",
        "fail",
        "failure",
        "broken",
        "disaster",
        "ugly",
        "cry",
        "depressed",
        "unhappy",
        "wrong",
    ]

    # handle negation phrases first
    negative_phrases = [
        "not good",
        "not happy",
        "not great",
        "not nice",
        "could be better",
    ]

    positive_phrases = ["not bad", "pretty good", "very good"]

    for phrase in negative_phrases:
        if phrase in text:
            return "sad"

    for phrase in positive_phrases:
        if phrase in text:
            return "happy"

    positive_score = 0
    negative_score = 0

    for word in happy_keywords:
        if word in text:
            positive_score += 1

    for word in sad_keywords:
        if word in text:
            negative_score += 1

    if positive_score > negative_score:
        return "happy"

    if negative_score > positive_score:
        return "sad"

    return "neutral"


@app.post("/sentiment")
def analyze_sentiment(data: SentimentRequest):

    results = []

    for sentence in data.sentences:
        results.append({"sentence": sentence, "sentiment": predict_sentiment(sentence)})

    return {"results": results}
