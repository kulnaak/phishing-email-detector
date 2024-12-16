import joblib
from pydantic import BaseModel

model = joblib.load("models/phishing_detector.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

class EmailData(BaseModel):
    email_body: str

def predict_email(email_data: EmailData) -> dict:
    """
    Predict if the given email text is phishing or safe.
    
    Args:
        email_data (EmailData): A structured input containing email body.
    
    Returns:
        dict: Prediction result including status and details.
    """
    try:
        input_vector = vectorizer.transform([email_data.email_body])
        
        prediction = model.predict(input_vector)[0]
        
        return {
            "email_body": email_data.email_body,
            "prediction": "Phishing" if prediction == 1 else "Safe"
        }
    except Exception as e:
        return {
            "error": f"Error during prediction: {str(e)}"
        }
