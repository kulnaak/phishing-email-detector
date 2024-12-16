from fastapi import APIRouter
from models.email_model import EmailData
from services import analyze_attachments, analyze_metadata, analyze_text, analyze_urls

router = APIRouter()

@router.post("/analyze/")
def analyze_email(email_data: EmailData):
    return {
        "attachment_results": analyze_attachments(email_data),
        "metadata_results": analyze_metadata(email_data),
        "text_results": analyze_text(email_data.email_body),
        "url_results": analyze_urls(email_data),
    }