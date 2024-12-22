from fastapi import APIRouter
import joblib
from models.email_model import EmailData

router = APIRouter()

@router.post("/predict/")
def predict_email(email_data: EmailData):
    try:
        model = joblib.load("models/phishing_email_detector.pkl")
        vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

        if model is None or vectorizer is None:
            return {"error": "Model or vectorizer not loaded"}
        
        email_body = email_data.email_body
        transformed_body = vectorizer.transform([email_body])
        prediction = model.predict(transformed_body)[0]
        result = "Фишинг" if prediction == 1 else "Аюулгүй"
        return {"prediction": result}
    except Exception as e:
        return {"error": str(e)}

