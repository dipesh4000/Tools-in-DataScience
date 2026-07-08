# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello from local FastAPI"}

@app.get("/health")
def health():
    return {"status": "ok"}