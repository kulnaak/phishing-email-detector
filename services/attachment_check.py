import os
import re
from typing import Dict, List, Union
from pydantic import BaseModel

DANGEROUS_EXTENSIONS = [".exe", ".js", ".zip", ".bat", ".scr", ".vbs", ".cmd"]

class EmailData(BaseModel):
    sender_email: str
    email_headers: str
    email_body: str
    attachments: List[str] = []

def check_file_type(file_name: str) -> str:
    try:
        _, extension = os.path.splitext(file_name)
        if extension.lower() in DANGEROUS_EXTENSIONS:
            return f"Suspicious file type detected: {extension}"
        return f"File type {extension} seems safe."
    except Exception as e:
        return f"Error checking file type: {e}"

def scan_file_content(file_name: str) -> str:
    try:
        suspicious_patterns = [
            r"<script>.*</script>",  
            r"powershell",           
            r"cmd.exe",              
            r"eval\(",               
            r"base64,",              
        ]
        for pattern in suspicious_patterns:
            if re.search(pattern, file_name, re.IGNORECASE):
                return f"Suspicious content detected matching pattern: {pattern}"
        return "No suspicious content found."
    except Exception as e:
        return f"Error scanning file content: {e}"

def analyze_attachments(email_data: EmailData) -> Dict[str, Union[str, Dict[str, str]]]:
    if not email_data.attachments:
        return {"attachment_analysis": "No attachments found."}

    analysis_results = {}
    for attachment in email_data.attachments:
        file_type_result = check_file_type(attachment)
        file_content_result = scan_file_content(attachment)
        analysis_results[attachment] = {
            "file_type_check": file_type_result,
            "file_content_check": file_content_result
        }
    
    return {"attachment_analysis": analysis_results}


# email_data = EmailData(
#     sender_email="example@example.com",
#     email_headers="Received: from example.com ([192.168.1.1])",
#     email_body="This email contains attachments.",
#     attachments=["malware.js", "safe.pdf", "suspicious.exe"]
# )

# results = analyze_attachments(email_data)
# print(results)
