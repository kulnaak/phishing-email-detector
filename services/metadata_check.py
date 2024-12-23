import dns.resolver
import re
import ipaddress
from typing import Dict, Union
from pydantic import BaseModel
from typing import List, Optional

class EmailData(BaseModel):
    sender_email: str
    email_headers: str
    cc_emails: Optional[List[str]] = None
    bcc_emails: Optional[List[str]] = None

def check_sender_domain(domain: str) -> str:
    try:
        domain = domain.strip("><")
        mx_records = dns.resolver.resolve(domain, 'MX') # DNS-ээс MX бичиглэлийг шалгаж байна
        return "MX бичиглэлтэй баталгаатай домайн" if mx_records else "Баталгаагүй домайн."
    except Exception as e:
        return f"Алдаа гарлаа: {e}"

def check_spf(domain: str) -> str:
    try:
        domain = domain.strip("><")  # Remove extraneous characters
        txt_records = dns.resolver.resolve(domain, 'TXT')
        for record in txt_records:
            if 'v=spf1' in record.to_text():
                return f"SPF бичиглэл олдсон: {record.to_text()}"
        return "SPF бичиглэл олдоогүй"
    except dns.resolver.NXDOMAIN:
        return f"Алдаа гарлаа: Домайн олдсонгүй: {domain}"
    except dns.resolver.Timeout:
        return f"Алдаа гарлаа: DNS хариу өгөхгүй байна: {domain}"
    except Exception as e:
        return f"Алдаа гарлаа: {e}"

def check_dkim(domain: str) -> str:
    try:
        dkim_selector = f"default._domainkey.{domain}"
        dkim_record = dns.resolver.resolve(dkim_selector, 'TXT')
        return f"DKIM бичиглэл олдсон: {dkim_record[0].to_text()}"
    except dns.resolver.NXDOMAIN:
        return "DKIM бичиглэл олдоогүй"
    except Exception as e:
        return f"Алдаа гарлаа. {e}"

def extract_sender_ip(email_headers: str) -> str:
    try:
        match = re.search(r"Received: from .* \[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]", email_headers)
        if match:
            ip = match.group(1)
            ipaddress.ip_address(ip)  # Validate IP
            return f"Баталгаатай илгээгчийн IP хаяг: {ip}"
        return "Баталгаагүй IP хаягаас илгээсэн."
    except Exception as e:
        return f"Алдаа гарлаа: {e}"

def analyze_metadata(email_data: EmailData) -> Dict[str, Union[str, Dict[str, str]]]:
    try:
        sender_domain = email_data.sender_email.split("@")[-1]
        
        return {
            "mx_check": check_sender_domain(sender_domain),
            "spf_check": check_spf(sender_domain),
            "dkim_check": check_dkim(sender_domain),
            "sender_ip_analysis": extract_sender_ip(email_data.email_headers)   
        }
    
    except Exception as e:
        return {"error": f"Алдаа гарлаа: {e}"}