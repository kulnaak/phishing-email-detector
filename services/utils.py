import pandas as pd
from urllib.parse import urlparse
from typing import List, Dict, Union
from pydantic import BaseModel

class EmailData(BaseModel):
    sender_email: str
    subject: str
    email_body: str

def extract_email_features(email: EmailData, phishing_keywords: List[str] = None) -> Dict[str, Union[str, int]]:
    phishing_keywords = phishing_keywords or ['verify', 'urgent', 'click here']
    
    sender_domain = get_domain_from_email(email.sender_email)
    subject_length = len(email.subject)
    num_urls = email.email_body.count('http')
    contains_keywords = 1 if any(keyword in email.email_body.lower() for keyword in phishing_keywords) else 0
    url_length = len(urlparse(email.email_body).path) if 'http' in email.email_body else 0
    
    return {
        "sender_domain": sender_domain,
        "subject_length": subject_length,
        "num_urls": num_urls,
        "contains_keywords": contains_keywords,
        "url_length": url_length
    }

def extract_features_from_dataframe(data: pd.DataFrame, phishing_keywords: List[str] = None) -> pd.DataFrame:
    phishing_keywords = phishing_keywords or ['verify', 'urgent', 'click here']
    data['sender_domain'] = data['sender_email'].apply(get_domain_from_email)
    data['subject_length'] = data['subject'].apply(len)
    data['num_urls'] = data['email_body'].apply(lambda x: x.count('http'))
    data['contains_keywords'] = data['email_body'].apply(
        lambda x: 1 if any(keyword in x.lower() for keyword in phishing_keywords) else 0
    )
    data['url_length'] = data['email_body'].apply(
        lambda x: len(urlparse(x).path) if 'http' in x else 0
    )
    return data

def get_domain_from_email(email: str) -> str:
    return email.split('@')[-1]
