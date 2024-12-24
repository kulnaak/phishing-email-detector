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
from routes.analyze_and_predict import analyze_and_predict
from routes.analyze import analyze_email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.generator import BytesGenerator
import io

app = FastAPI()

# IMAP серверийн тохиргоо
IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "turuu021125@gmail.com"
EMAIL_PASSWORD = "lmzu mpuk hsel opib" # lmzu mpuk hsel opib

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
        
# Имэйлын их биеийг өөрчлөх функц
def modify_email_body(raw_email, analysis_results):
    """Modify the email body to append the analysis results."""
    original_email = email.message_from_bytes(raw_email)

    modified_email = MIMEMultipart()
    for header in ["From", "To", "Subject", "Message-ID"]:
        if original_email[header]:
            modified_email[header] = original_email[header]

    body = ""
    if original_email.is_multipart():
        for part in original_email.get_payload():
            if part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True).decode()
                modified_html_body = html_body + f"<br><br><strong>--- Analysis Results ---</strong><br>{analysis_results}"
                modified_email.attach(MIMEText(modified_html_body, "html"))
            else:
                modified_email.attach(part)
    else:
        body = original_email.get_payload(decode=True).decode()
        modified_body = body + f"\n\n--- Analysis Results ---\n{analysis_results}"
        modified_email.attach(MIMEText(modified_body, "plain"))

    buffer = io.BytesIO()
    BytesGenerator(buffer).flatten(modified_email)
    return buffer.getvalue()
    
# Имэйл дахин оруулах функц
def reupload_modified_email(imap, folder, modified_email):
    """Upload the modified email to a specified folder."""
    response = imap.append(folder, None, None, modified_email)
    if response[0] == "OK":
        print(f"Modified email successfully uploaded to {folder}")
    else:
        print(f"Failed to upload modified email to {folder}. Response: {response}")
    
# Имэйл боловсруулах функц
def process_email_with_analysis(email_data: EmailData, analysis_results):
    """Fetch, modify, and reupload the email with appended analysis."""
    imap = connect_to_imap()
    try:
        imap.select("INBOX")
        result, data = imap.search(None, f'(HEADER Message-ID "{email_data.message_id}")')

        if result == "OK":
            uids = data[0].split()
            if not uids:
                print(f"No email found with Message-ID: {email_data.message_id}")
                return

            raw_email = fetch_email(imap, uids[0])
            if not raw_email:
                print(f"Failed to fetch email with UID {uids[0]}")
                return

            modified_email = modify_email_body(raw_email, analysis_results)

            reupload_modified_email(imap, "Phishing", modified_email)

            imap.store(uids[0], "+FLAGS", "\\Deleted")
            imap.expunge()
            print(f"Appended analysis to email and reuploaded to the 'Phishing' folder.")

    except Exception as e:
        print(f"Error processing email with analysis: {e}")
    finally:
        imap.logout()
        
# Имэйл татаж авах функц
def fetch_email(imap, uid):
    """Fetch the raw email data by UID."""
    _, msg_data = imap.fetch(uid, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            return response_part[1] 
    return None
    
# Анализ хийх болон өөрчлөх
def send_to_analyze_and_predict(email_data: EmailData):
    try:
        print(f"Sending email for analysis: {email_data.sender_email}, Subject: {email_data.subject}")
        response_data = analyze_and_predict(email_data)

        print("Analysis and Prediction Response:", response_data)

        prediction = response_data.get("prediction_results", {}).get("prediction")
        analysis_results = response_data.get("analysis_results", {})
        
        if isinstance(analysis_results, dict):
            analysis_results["prediction"] = prediction
        else:
            analysis_results = {"prediction": prediction}

        analysis_results_str = "\n".join([f"{key}: {value}" for key, value in analysis_results.items()])


        if prediction == "Фишинг":
            # analysis_results_str = "\n".join([f"{key}: {value}" for key, value in analysis_results.items()])
            print("Фишинг имэйл илэрлээ. Spam фолдер руу шилжүүлж байна.")
            process_email_with_analysis(email_data, analysis_results_str)
        elif prediction == "Аюулгүй":
            print("Имэйл аюулгүй байна. Inbox дотор үлдээж байна.")
        else:
            print(f"Unexpected prediction result: {prediction}. Email will not be moved.")
    except Exception as e:
        print(f"Error calling analyze-and-predict: {e}")

# Имэйлын агуулгыг задлах функц
def parse_email(raw_email):
    msg = email.message_from_bytes(raw_email)
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else "utf-8")
    sender = msg.get("From")
    message_id = msg.get("Message-ID")
    print(f"Message-ID:::::::::::::::::::::::::::::::::::::::::::::: {message_id}")

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
    
    email_data = EmailData(
        sender_email=sender,
        email_headers=email_headers,
        email_body=body,
        subject=subject,
        attachments=[],
        urls=[],
        message_id=message_id,
    )
    
    return email_data

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
                                
                                if email_data.analysis_results:
                                    print(f"Analysis Results: {email_data.analysis_results}")
                                
                                send_to_analyze_and_predict(email_data)

            imap.noop()
            time.sleep(5)

        except imaplib.IMAP4.abort:
            print("IMAP disconnected. Retrying to connect...")
            imap = connect_to_imap()
        except Exception as e:
            print(f"Error: {e}. Retrying about 5 seconds later...")
            time.sleep(5)
            

# def send_to_analyze_and_predict(email_data: EmailData):
#     try:
#         # Call the analyze_and_predict function directly
#         print(f"Sending email for analysis: {email_data.sender_email}, Subject: {email_data.subject}")
#         response_data = analyze_and_predict(email_data)

#         print("Analysis and Prediction Response:", response_data)

#         # Extract the prediction
#         prediction = response_data.get("prediction_results", {}).get("prediction")

#         # Check prediction result
#         if prediction == "Фишинг":
#             print(f'email_data.email_body: {email_data.email_body}')
#             print("Фишинг имэйл илэрлээ. Spam фолдер руу шилжүүлж байна.")
#             move_to_spam_folder(email_data)
#         elif prediction == "Аюулгүй":
#             print(f'email_data.email_body: {email_data.email_body}')
#             print("Имэйл аюулгүй байна. Inbox дотор үлдээж байна.")
#         else:
#             print(f"Unexpected prediction result: {prediction}. Email will not be moved.")
#     except Exception as e:
#         print(f"Error calling analyze-and-predict: {e}")

def move_to_spam_folder(email_data: EmailData):
    if not email_data.message_id:
        print("Message-ID is missing. Cannot move email to Spam.")
        return

    imap = connect_to_imap()
    try:
        result, data = imap.search(None, f'(HEADER Message-ID "{email_data.message_id}")')
        
        if result == "OK":
            email_ids = data[0].split()
            if not email_ids:
                print(f"No email found with Message-ID: {email_data.message_id}")
                return
            
            for num in email_ids:
                if "MOVE" in imap.capabilities:
                    result_move = imap.uid("MOVE", num, "Phishing")
                    
                    if result_move[0] == "OK":
                        print(f"Successfully moved email with Message-ID {email_data.message_id} to Spam.")
                    else:
                        print(f"Failed to move email with Message-ID {email_data.message_id}.")
                else:
                    imap.store(num, '+X-GM-LABELS', 'Phishing')
                    imap.store(num, '+FLAGS', r'\Deleted')
                    print(f"Marked email with Message-ID {email_data.message_id} as Phishing.")
            
            imap.expunge()
        else:
            print(f"Failed to search for Message-ID {email_data.message_id}. Status: {result}")
    except Exception as e:
        print(f"Error moving email to Phishing: {e}")
    finally:
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