import dns.resolver
import re
import ipaddress

def check_sender_domain(domain):
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return "Valid domain with MX records" if mx_records else "Invalid domain"
    except Exception as e:
        return f"Domain check error: {e}"

def check_spf(domain):
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        for record in txt_records:
            if 'v=spf1' in record.to_text():
                return f"SPF record found: {record.to_text()}"
        return "No SPF record found"
    except Exception as e:
        return f"SPF check error: {e}"

def check_dkim(domain):
    try:
        dkim_selector = f"default._domainkey.{domain}"
        dkim_record = dns.resolver.resolve(dkim_selector, 'TXT')
        return f"DKIM record found: {dkim_record[0].to_text()}"
    except dns.resolver.NXDOMAIN:
        return "No DKIM record found"
    except Exception as e:
        return f"DKIM check error: {e}"


def extract_sender_ip(email_headers):
    try:
        match = re.search(r"Received: from .* \[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]", email_headers)
        if match:
            ip = match.group(1)
            ipaddress.ip_address(ip)  # Validate IP
            return f"Valid sender IP: {ip}"
        return "No valid sender IP found"
    except Exception as e:
        return f"IP extraction error: {e}"
