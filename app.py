from fastapi import FastAPI
from routes import email_analysis

app = FastAPI()

app.include_router(email_analysis.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Phishing Email Detector API"}
