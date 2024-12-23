from fastapi import APIRouter
import joblib
from models.email_model import EmailData
from services.utils import detect_language_override, translate_text

router = APIRouter()

@router.post("/predict/")
def predict_email(email_data: EmailData):
    try:
        model = joblib.load("models/phishing_email_detector.pkl")
        vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

        if model is None or vectorizer is None:
            return {"error": "Model or vectorizer not loaded"}
        
        email_body = email_data.email_body
        
        detected_language = detect_language_override(email_body)

        if detected_language != "en":
            email_body = translate_text(email_body, detected_language, "en")
        
        transformed_body = vectorizer.transform([email_body])
        prediction = model.predict(transformed_body)[0]
        result = "Фишинг" if prediction == 1 else "Аюулгүй"
        return {
            "prediction": result
        }
    except Exception as e:
        return {"error": str(e)}

