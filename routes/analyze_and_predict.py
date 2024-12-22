from fastapi import APIRouter
from routes.analyze import analyze_email
from routes.predict import predict_email
from models.email_model import EmailData

router = APIRouter()

@router.post("/analyze-and-predict/")
def analyze_and_predict(email_data: EmailData):
    try:
        analysis_results = analyze_email(email_data)
        print(f'Model is::: {analysis_results}')
        prediction_results = predict_email(email_data)
        print(f'Model is::: {prediction_results}')
        return {
            "analysis_results": analysis_results,
            "prediction_results": prediction_results,
        }
    except Exception as e:
        return {"error": str(e)}
    