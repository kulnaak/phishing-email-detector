from fastapi import FastAPI
from routes import email_analysis
from models.email_model import EmailData
from services.metadata_check import check_sender_domain, check_spf, check_dkim, extract_sender_ip
import joblib

app = FastAPI()

app.include_router(email_analysis.router)

@app.on_event("startup")
def load_resources():
    global model, vectorizer
    model = joblib.load("models/phishing_detector.pkl")
    vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Phishing Email Detector API"}

@app.post("/predict/")
def detect_phishing(email_data: EmailData):
    try:
        email_body = email_data.email_body
        transformed_body = vectorizer.transform([email_body])
        
        prediction = model.predict(transformed_body)[0]
        result = "Phishing" if prediction == 1 else "Safe"
        
        return {
            "sender_email": email_data.sender_email,
            "email_headers": email_data.email_headers,
            "prediction": result
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

@app.post("/analyze/")
def analyze_combined(email_data: EmailData, mode: str = "combined"):
    try:
        sender_email = email_data.sender_email
        email_headers = email_data.email_headers
        email_body = email_data.email_body
        domain = sender_email.split('@')[-1]

        metadata_results = {
            "domain_check": check_sender_domain(domain),
            "spf_check": check_spf(domain),
            "dkim_check": check_dkim(domain),
            "sender_ip_check": extract_sender_ip(email_headers),
        }

        transformed_body = vectorizer.transform([email_body])
        prediction = model.predict(transformed_body)[0]
        ml_result = "Phishing" if prediction == 1 else "Safe"

        if mode == "metadata-only":
            return {"metadata_analysis": metadata_results}
        elif mode == "ml-only":
            return {"ml_prediction": ml_result}
        elif mode == "combined":
            return {
                "metadata_analysis": metadata_results,
                "ml_prediction": ml_result
            }
        else:
            return {"error": "Invalid mode. Use 'metadata-only', 'ml-only', or 'combined'."}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
