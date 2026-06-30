from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import csv
from pathlib import Path
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

with open(Path(__file__).parent / "q-fastapi.csv") as f:
    students = [{"studentId": int(r["studentId"]), "class": r["class"]} for r in csv.DictReader(f)]

@app.get("/api")
def get_students(class_: Optional[List[str]] = Query(None, alias="class")):
    if class_:
        return {"students": [s for s in students if s["class"] in class_]}
    return {"students": students}
