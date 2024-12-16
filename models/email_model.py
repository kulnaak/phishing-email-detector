from pydantic import BaseModel, Field
from typing import Optional, List

class EmailData(BaseModel):
    sender_email: str = Field(..., description="The email address of the sender")
    sender_name: Optional[str] = Field(None, description="The display name of the sender")
    recipient_email: Optional[str] = Field(None, description="The email address of the recipient")
    cc_emails: Optional[List[str]] = Field(None, description="List of CC'd email addresses")
    bcc_emails: Optional[List[str]] = Field(None, description="List of BCC'd email addresses")
    subject: Optional[str] = Field(None, description="The subject of the email")
    email_body: str = Field(..., description="The full text or HTML content of the email body")
    email_headers: str = Field(..., description="The raw headers of the email")
    attachments: Optional[List[str]] = Field(None, description="List of attachment filenames")
    urls: Optional[List[str]] = Field(None, description="List of URLs found in the email body")
    timestamp: Optional[str] = Field(None, description="The date and time the email was sent")
    ip_addresses: Optional[List[str]] = Field(None, description="List of IP addresses found in the email headers")
    reply_to: Optional[str] = Field(None, description="The reply-to email address if specified")

