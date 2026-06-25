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
            students.append({"studentId": int(row["studentId"]), "class": row["class"]})

    return students


@app.get("/api")
def get_students(class_: list[str] | None = Query(default=None, alias="class")):
    students = load_students()

    if class_:
        students = [s for s in students if s["class"] in class_]

    return {"students": students}
