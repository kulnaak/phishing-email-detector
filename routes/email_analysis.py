from fastapi import APIRouter
from models.email_model import EmailData
from services.metadata_check import check_sender_domain, check_spf, check_dkim, extract_sender_ip

router = APIRouter()

@router.post("/analyze-email")
def analyze_email(email_data: EmailData):
    sender_email = email_data.sender_email
    email_headers = email_data.email_headers
    domain = sender_email.split('@')[-1]

    results = {
        "domain_check": check_sender_domain(domain),
        "spf_check": check_spf(domain),
        "dkim_check": check_dkim(domain),
        "sender_ip_check": extract_sender_ip(email_headers),
    }
    
    return results
