'''import json
import statistics

with open("c:\\Users\\naija\\Downloads\\q-calculate-variance.json", "r") as f:
    data = json.load(f)

answer = statistics.variance(data)

print(round(answer, 2))

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import re

START = "https://sanand0.github.io/tdsdata/crawl_html/"

visited = set()
queue = deque([START])

count = 0

while queue:
    url = queue.popleft()

    if url in visited:
        continue

    visited.add(url)

    try:
        r = requests.get(url, timeout=5)
        if "text/html" not in r.headers.get("content-type", ""):
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        path = urlparse(url).path
        filename = path.split("/")[-1]

        if re.match(r'^[A-Ka-k].*\.html?$', filename):
            count += 1

        for a in soup.find_all("a", href=True):
            nxt = urljoin(url, a["href"])

            if nxt.startswith(START):
                if nxt not in visited:
                    queue.append(nxt)

    except:
        pass

print("Count:", count)
print("Visited:", len(visited))'''


from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import csv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_FILE = "q-fastapi.csv"


def load_students():
    students = []

    with open(CSV_FILE, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            students.append({
                "studentId": int(row["studentId"]),
                "class": row["class"]
            })

    return students


@app.get("/api")
def get_students(class_: list[str] | None = Query(default=None, alias="class")):
    students = load_students()

    if class_:
        students = [
            s for s in students
            if s["class"] in class_
        ]

    return {"students": students}