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
        mx_records = dns.resolver.resolve(domain, 'MX') # DNS-ээс MX бичиглэлийг шалгаж байна
        return "Valid domain with MX records" if mx_records else "Invalid domain"
    except Exception as e:
        return f"Domain check error: {e}"

def check_spf(domain: str) -> str:
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        for record in txt_records:
            if 'v=spf1' in record.to_text():
                return f"SPF record found: {record.to_text()}"
        return "No SPF record found"
    except Exception as e:
        return f"SPF check error: {e}"

def check_dkim(domain: str) -> str:
    try:
        dkim_selector = f"default._domainkey.{domain}"
        dkim_record = dns.resolver.resolve(dkim_selector, 'TXT')
        return f"DKIM record found: {dkim_record[0].to_text()}"
    except dns.resolver.NXDOMAIN:
        return "No DKIM record found"
    except Exception as e:
        return f"DKIM check error: {e}"

def extract_sender_ip(email_headers: str) -> str:
    try:
        match = re.search(r"Received: from .* \[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]", email_headers)
        if match:
            ip = match.group(1)
            ipaddress.ip_address(ip)  # Validate IP
            return f"Valid sender IP: {ip}"
        return "No valid sender IP found"
    except Exception as e:
        return f"IP extraction error: {e}"

def analyze_email_sender(email_data: EmailData) -> Dict[str, Union[str, Dict[str, str]]]:
    try:
        sender_domain = email_data.sender_email.split("@")[-1]
        
        domain_result = {
            "mx_check": check_sender_domain(sender_domain),
            "spf_check": check_spf(sender_domain),
            "dkim_check": check_dkim(sender_domain)
        }

        sender_ip_result = extract_sender_ip(email_data.email_headers)

        return {
            "sender_domain_analysis": domain_result,
            "sender_ip_analysis": sender_ip_result
        }
    except Exception as e:
        return {"error": f"Error analyzing sender details: {e}"}
