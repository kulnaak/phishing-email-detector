from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Union

class EmailData(BaseModel):
    sender_email: str = Field(..., description="Илгээгчийн имейл хаяг")
    sender_name: Optional[str] = Field(None, description="Илгээгчийн нэр")
    recipient_email: Optional[str] = Field(None, description="Хүлээн авагчийн имейл хаяг")
    cc_emails: Optional[List[str]] = Field(None, description="СС хаягууд")
    bcc_emails: Optional[List[str]] = Field(None, description="BCC хаягууд")
    subject: Optional[str] = Field(None, description="Имейлийн гарчиг")
    email_body: str = Field(..., description="Имейлийн их бие хэсэг буюу гол агуулга")
    email_headers: str = Field(..., description="Имейлийн толгой хэсэг")
    attachments: Optional[List[str]] = Field(None, description="Хавсралтууд")
    urls: Optional[List[str]] = Field(None, description="Имейл доторх линкүүд")
    timestamp: Optional[str] = Field(None, description="Имейл илгээсэн цаг")
    ip_addresses: Optional[List[str]] = Field(None, description="Имейлийн толгой хэсэгт орсон IP хаягууд")
    reply_to: Optional[str] = Field(None, description="Хариу илгээх хаяг")
    message_id: Optional[str] = Field(None, description="Имейлийн Message-ID")
    
    analysis_results: Optional[Dict[str, Union[str, Dict[str, str]]]] = None

    class Config:
        allow_mutation = True

