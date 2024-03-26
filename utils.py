import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from smtplib import SMTP
from datetime import datetime, timedelta

json_db_file = 'users_db.json'

def load_data():
    if os.path.exists(json_db_file):
        with open(json_db_file, 'r') as file:
            data = json.load(file)
            print("Loaded data:", data)  # Add this line for debugging
            return data
    return {}


def save_data(data):
    with open(json_db_file, 'w') as file:
        json.dump(data, file, indent=4)

def find_user(account_id, users_db):
    return users_db.get(account_id)

def send_email(recipient, subject, body, attachment=None):
    sender_email = "jguimfackjeuna@smail.hs-bremerhaven.de"
    sender_password = "Jeunaj3"
    smtp_host = 'smail.hs-bremerhaven.de'
    smtp_port = 587
    user_id = "jguimfackjeuna"

    if recipient is None or sender_email is None or sender_password is None:
        raise ValueError("Email credentials are not set.")

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient
    message['Subject'] = subject

    # Attach body
    message.attach(MIMEText(body, 'plain'))

    # Attach file if provided
    if attachment:
        with open(attachment, 'rb') as file:
            part = MIMEApplication(file.read(), Name=os.path.basename(attachment))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
            message.attach(part)

    try:
        with SMTP(smtp_host, smtp_port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(user_id, sender_password)
            smtp.sendmail(sender_email, recipient, message.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")
