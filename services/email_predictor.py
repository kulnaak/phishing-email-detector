import joblib
from pydantic import BaseModel

# Load the saved model and vectorizer
model = joblib.load("phishing_email_detector.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

class EmailData(BaseModel):
    email_body: str

def predict_email(email_data: EmailData) -> dict:
    """
    SVM моделийг ашиглан тухайн имейлийг фишинг эсэхийг таамаглана.
    
    Args:
        email_data (EmailData): Имейлийн их бие хэсэг буюу гол агуулга..
    
    Returns:
        dict: Үр дүн.
    """
    try:
        input_vector = vectorizer.transform([email_data.email_body])
        prediction = model.predict(input_vector)[0]
        
        return {
            "email_body": email_data.email_body,
            "prediction": "Фишинг" if prediction == 1 else "Аюулгүй"
        }
    except Exception as e:
        return {
            "error": f"Алдаа гарлаа. {str(e)}"
        }
