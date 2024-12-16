from pydantic import BaseModel

class EmailData(BaseModel):
    sender_email: str
    email_headers: str
