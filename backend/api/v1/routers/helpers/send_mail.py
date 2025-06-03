import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os
import random
import string
import time
from jinja2 import Environment, FileSystemLoader
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from ...database import models

otp_store = {}
env = load_dotenv('.env')
templates = Environment(loader=FileSystemLoader('templates'))

def render_template(template_name, context):
    template = templates.get_template(template_name)
    return template.render(context) 

def generate_otp(email: str, expiry_seconds: int = 300) -> str:
    otp = ''.join(random.choices(string.digits, k=6))
    otp_store[email] = {"otp": otp, "timestamp": time.time(), "expiry": expiry_seconds}
    return str(otp)

def verify_otp(email: str, submitted_otp: str) -> bool:
    record = otp_store.get(email)
    if not record:
        return False  # No OTP found

    if time.time() - record["timestamp"] > record["expiry"]:
        return False  # OTP expired

    if record["otp"] != submitted_otp:
        return False  # Invalid OTP

    return True

def send_mail(data: models.MailRequest):
    sender_email = "access@advancex.ai"
    recipient = data.recipient_email
    options = data.mail_options
    context = data.mail_context

    # Validation
    if options.otp and not context.otp:
        raise ValueError("OTP is enabled in options but not provided in context.")
    if options.tnc and not context.tnc_location:
        raise ValueError("T&C is enabled in options but tnc_location is not provided.")
    if options.invoice and not context.invoice_location:
        raise ValueError("Invoice is enabled in options but invoice_location is not provided.")

    subject = None
    body_html = None

    client = boto3.client(
        service_name='ses',
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    # OTP Email
    if options.otp:
        print("Sending OTP Mail")
        otp_code = context.otp
        subject = f"ADX Data Portal - OTP - {otp_code}"
        body_html = render_template("otp_mail.html", {"otp": otp_code})

    # Waitlist Email
    elif options.waitlist:
        print("Sending waitlist Mail")
        subject = "ADX Data Portal - Welcome to ADX Data Portal"
        body_html = render_template("waitlist.html", {"data": None})

    # Confirmation Email
    elif options.confirmation:
        print("Sending confirmation Mail")
        dashboard_url = "https://advancex.ai/"
        subject = "ADX Data Portal - Activation Email"
        body_html = render_template("confirmation.html", {"dashboard_url": dashboard_url})

    # Send email without attachment
    if subject and body_html:
        try:
            response = client.send_email(
                Source=sender_email,
                Destination={'ToAddresses': [recipient]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Html': {'Data': body_html}}
                }
            )
            print("Email sent! Message ID:", response['MessageId'])
        except ClientError as e:
            print("Error sending email:", e.response['Error']['Message'])



    # T&C Email with Attachment
    if options.tnc:
        print("Sending T&C Mail with Attachment")

        subject = "ADX Data Portal - Terms and Conditions"
        body_html = render_template("tnc.html", {})

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient

        msg.attach(MIMEText(body_html, "html"))

        attachment_path = context.tnc_location  # Use dynamic path from context
        try:
            with open(attachment_path, "rb") as file:
                part = MIMEApplication(file.read())
                part.add_header("Content-Disposition", "attachment", filename=os.path.basename(attachment_path))
                msg.attach(part)
        except Exception as e:
            print("Failed to attach T&C file:", e)
            return

        try:
            response = client.send_raw_email(
                Source=sender_email,
                Destinations=[recipient],
                RawMessage={"Data": msg.as_string()}
            )
            print("T&C Email with attachment sent! Message ID:", response['MessageId'])
        except ClientError as e:
            print("Error sending T&C email:", e.response['Error']['Message'])

