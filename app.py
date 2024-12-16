from fastapi import FastAPI
from routes import *
from models.email_model import EmailData

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Unified Phishing Email Detector API"}

@app.post("/analyze-and-predict/")
def analyze_and_predict(email_data: EmailData):
    try:
        analysis_results = analyze_email(email_data)
        prediction_results = predict_email(email_data)
        combined_results = {
            "analysis_results": analysis_results,
            "prediction_results": prediction_results
        }
        return combined_results
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
