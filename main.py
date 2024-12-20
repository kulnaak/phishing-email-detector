# Бид fastapi хэрэгсэл болон имэйл шалгахын тулд imap, email, threading-ийг ашиглана.
import imaplib
import email
from email.header import decode_header
from pydantic import BaseModel
from fastapi import FastAPI
from typing import List
import threading
import time
import requests

from services.utils import load_resources, model, vectorizer

from routes import analyze_and_predict_router, analyze_router, predict_router

from models.email_model import EmailData

app = FastAPI()

# IMAP серверийн тохиргоо
IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "turuu021125@gmail.com"
EMAIL_PASSWORD = "lmzu mpuk hsel opib" # lmzu mpuk hsel opib

# Real-time email storage
new_emails: List[EmailData] = []
processed_uids = set()   # Үргэлжлүүлэн боловсруулсан UID-уудыг хадгалах

# IMAP серверт холбогдох функц
def connect_to_imap():
    """IMAP серверт холбогдох функц"""
    try:
        print("Connecting IMAP server...")
        imap = imaplib.IMAP4_SSL(IMAP_SERVER)
        imap.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        imap.select("INBOX")
        print("Successfully connected to IMAP server.")
        return imap
    except Exception as e:
        print(f"Error for connecting IMAP server: {e}")
        time.sleep(5)
        return connect_to_imap()

# Имэйлын агуулгыг задлах функц
def parse_email(raw_email):
    """Extract and parse email content."""
    msg = email.message_from_bytes(raw_email)
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else "utf-8")
    sender = msg.get("From")

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")
    else:
        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

    email_headers = "\n".join([f"{k}: {v}" for k, v in msg.items()])
    
    # Ensure all required fields are populated
    return EmailData(
        sender_email=sender,
        email_headers=email_headers,
        email_body=body,
        subject=subject,
        attachments=[],
        urls=[]
    )

# Реал цагийн имэйл мониторинг
def monitor_inbox():
    """Polling механизм ашиглан имэйл шалгах"""
    global new_emails, processed_uids
    imap = connect_to_imap()

    while True:
        try:
            print("Checking new email...")
            status, messages = imap.search(None, "UNSEEN")
            if status == "OK":
                uids = messages[0].split()
                print(f"{len(uids)} new mail found.")
                for uid in uids:
                    if uid not in processed_uids:
                        _, msg_data = imap.fetch(uid, "(RFC822)")
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                email_data = parse_email(response_part[1])
                                new_emails.append(email_data)
                                processed_uids.add(uid)
                                print(f"Found a new mail: {email_data}")
                                
                                send_to_analyze_and_predict(email_data)

            imap.noop()
            time.sleep(5)

        except imaplib.IMAP4.abort:
            print("IMAP disconnected. Retrying to connect...")
            imap = connect_to_imap()
        except Exception as e:
            print(f"Error: {e}. Retrying about 5 seconds later...")
            time.sleep(5)
            
def send_to_analyze_and_predict(email_data: EmailData):
    """
    Шинэ имэйлийг analyze-and-predict endpoint рүү илгээх функц.
    """
    url = "http://127.0.0.1:8000/analysis-and-predict/analyze-and-predict/"
    try:
        # Имэйлийн мэдээллийг JSON болгон илгээх
        response = requests.post(url, json=email_data.dict())
        # Амжилттай илгээгдсэн хариуг хэвлэх
        if response.status_code == 200:
            print("Analysis and Prediction Response:", response.json())
            prediction = response.json().get("prediction_results", {}).get("prediction")
            if prediction == "Phishing":
                print("Phishing email detected and moved to spam folder.")
                move_to_spam_folder(email_data)
        else:
            print(f"Failed to call analyze-and-predict. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error calling analyze-and-predict: {e}")

def move_to_spam_folder(email_data: EmailData):
    imap = connect_to_imap()
    result, data = imap.search(None, f'(HEADER Message-ID "{email_data.email_headers}")')
    if result == "OK":
        for num in data[0].split():
            imap.store(num, '+X-GM-LABELS', '\\Spam')
            imap.expunge()
    imap.logout()

app.include_router(analyze_and_predict_router, prefix="/analysis-and-predict", tags=["Analysis and Prediction"])
app.include_router(analyze_router, prefix="/analyze", tags=["Analysis"])
app.include_router(predict_router, prefix="/predict", tags=["Prediction"])

@app.get("/real-time-emails", response_model=List[EmailData])
def get_new_emails():
    """API: Шинэ имэйлийг авах"""
    global new_emails
    emails = new_emails[:]
    new_emails.clear()
    return emails

@app.on_event("startup")
def start_monitoring():
    """Startup event дээр IMAP мониторинг эхлүүлэх"""
    load_resources()
    thread = threading.Thread(target=monitor_inbox, daemon=True)
    thread.start()

@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "IMAP Real-Time Email API is running"}