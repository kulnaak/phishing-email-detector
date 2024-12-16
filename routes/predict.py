from fastapi import APIRouter
from models.email_model import EmailData
from services.utils import model, vectorizer

router = APIRouter()

@router.post("/predict")
def predict_email(email_data: EmailData):
    try:
        email_body = email_data.email_body
        transformed_body = vectorizer.transform([email_body])
        
        prediction = model.predict(transformed_body)[0]
        result = "Phishing" if prediction == 1 else "Safe"
        
        return {
            # "sender_email": email_data.sender_email,
            # "email_headers": email_data.email_headers,
            "prediction": result
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}