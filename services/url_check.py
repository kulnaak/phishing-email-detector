import requests
from urllib.parse import urlparse
from typing import List, Dict, Union
from pydantic import BaseModel

class EmailData(BaseModel):
    email_body: str
    urls: List[str] = []

def analyze_domain(url: str) -> str:
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        suspicious_patterns = ["login", "verify", "secure", "-secure", "update", "нэвтрэх", "шалгах", "баталгаа", "засварлах", "нууц", "password", "pass", "auth"]	
        if any(pattern in domain for pattern in suspicious_patterns):
            return f"Сэжигтэй домайн илэрсэн: {domain}"
        return f"Аюулгүй домайн: {domain}"
    except Exception as e:
        return f"Алдаа гарлаа: {e}"

def expand_shortened_url(short_url: str) -> str:
    try:
        response = requests.head(short_url, allow_redirects=True)
        expanded_url = response.url
        return f"Өргөтгөсөн URL: {expanded_url}"
    except Exception as e:
        return f"Алдаа гарлаа: {e}"

def check_https(url: str) -> str:
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme == "https":
            return "HTTPS протокол ашигласан тул аюулгүй."
        return "HTTPS протокол ашиглаагүй тул аюултай байж болзошгүй."
    except Exception as e:
        return f"Алдаа гарлаа: {e}"

def analyze_urls(email_data: EmailData) -> Dict[str, Union[str, Dict[str, str]]]:
    if not email_data.urls:
        return {"url_analysis": "Линк агуулаагүй."}

    results = {}
    for url in email_data.urls:
        domain_analysis = analyze_domain(url)
        https_check = check_https(url)
        shortened_domains = ["bit.ly", "tinyurl.com", "t.co"]
        parsed_url = urlparse(url)
        if parsed_url.netloc in shortened_domains:
            expanded_url = expand_shortened_url(url)
        else:
            expanded_url = "Өргөтгөсөн URL биш."
        results[url] = {
            "domain_analysis": domain_analysis,
            "https_check": https_check,
            "shortened_url_expansion": expanded_url
        }
    return {"url_analysis": results}
