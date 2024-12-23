import pandas as pd
from urllib.parse import urlparse
from typing import List, Dict, Union
from models.email_model import EmailData
import joblib
from langdetect import detect
from translate import Translator

model = None
vectorizer = None

def load_resources():
    global model, vectorizer
    try:
        model = joblib.load("models/phishing_email_detector.pkl")
        print(f'Model is::: {model}')
        vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
        print(f'Vector is::: {vectorizer}')
        print("Resources loaded successfully!")
    except Exception as e:
        print(f"Error loading resources: {e}")
        
def detect_language_override(email_body: str) -> str:
    try:
        mongolian_specific_chars = ["ү", "ө", "х", "ч"]
        if any(char in email_body for char in mongolian_specific_chars):
            return "mn"

        detected_language = detect(email_body)

        return detected_language if detected_language in ["mn", "ru", "en"] else "en"
    except Exception as e:
        print(f"Error detecting language: {e}")
        return "en"
        
def translate_text(text: str, detected_language: str, target_language: str = "en") -> str:
    try:
        if detected_language == target_language:
            return text

        translator = Translator(from_lang=detected_language, to_lang=target_language)
        return translator.translate(text)
    except Exception as e:
        print(f"Error translating text: {e}")
        return text


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
