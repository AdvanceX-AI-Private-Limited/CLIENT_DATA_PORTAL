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
from logger import create_logger

# Initialize logger
logger = create_logger(__name__)
otp_store = {}
env = load_dotenv('.env')
templates = Environment(loader=FileSystemLoader('templates'))

def render_template(template_name, context):
    """Render email template with given context"""
    try:
        logger.info(f"Rendering template: {template_name}")
        template = templates.get_template(template_name)
        rendered_content = template.render(context)
        logger.info(f"Successfully rendered template: {template_name}")
        return rendered_content
    except Exception as e:
        logger.error(f"Failed to render template {template_name}: {str(e)}")
        raise

def generate_otp(email: str, expiry_seconds: int = 300) -> str:
    """Generate OTP for given email with expiry"""
    try:
        logger.info(f"Generating OTP for email: {email} with expiry: {expiry_seconds}s")
        otp = ''.join(random.choices(string.digits, k=6))
        otp_store[email] = {"otp": otp, "timestamp": time.time(), "expiry": expiry_seconds}
        logger.info(f"OTP generated successfully for email: {email}")
        logger.debug(f"OTP store now contains {len(otp_store)} entries")
        return str(otp)
    except Exception as e:
        logger.error(f"Failed to generate OTP for email {email}: {str(e)}")
        raise

def verify_otp(email: str, submitted_otp: str) -> bool:
    """Verify OTP for given email"""
    logger.info(f"Verifying OTP for email: {email}")
    
    record = otp_store.get(email)
    if not record:
        logger.warning(f"No OTP record found for email: {email}")
        return False

    current_time = time.time()
    time_elapsed = current_time - record["timestamp"]
    
    if time_elapsed > record["expiry"]:
        logger.warning(f"OTP expired for email: {email}. Elapsed time: {time_elapsed}s, Expiry: {record['expiry']}s")
        # Clean up expired OTP
        del otp_store[email]
        logger.info(f"Removed expired OTP for email: {email}")
        return False

    if record["otp"] != submitted_otp:
        logger.warning(f"Invalid OTP submitted for email: {email}")
        return False

    logger.info(f"OTP verified successfully for email: {email}")
    # Clean up used OTP
    del otp_store[email]
    logger.info(f"Removed used OTP for email: {email}")
    return True

def send_mail(data: models.MailRequest):
    """Send email based on mail request data"""
    logger.info(f"Starting email send process for recipient: {data.recipient_email}")
    
    sender_email = "access@advancex.ai"
    recipient = data.recipient_email
    options = data.mail_options
    context = data.mail_context

    logger.info(f"Email options - OTP: {options.otp}, Waitlist: {options.waitlist}, "
                f"Confirmation: {options.confirmation}, T&C: {options.tnc}")

    # Validation
    try:
        if options.otp and not context.otp:
            raise ValueError("OTP is enabled in options but not provided in context.")
        if options.tnc and not context.tnc_location:
            raise ValueError("T&C is enabled in options but tnc_location is not provided.")
        if options.invoice and not context.invoice_location:
            raise ValueError("Invoice is enabled in options but invoice_location is not provided.")
        
        logger.info("Email request validation passed")
    except ValueError as e:
        logger.error(f"Email request validation failed: {str(e)}")
        raise

    subject = None
    body_html = None

    # Initialize AWS SES client
    try:
        logger.info("Initializing AWS SES client")
        client = boto3.client(
            service_name='ses',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        logger.info(f"AWS SES client initialized for region: {os.getenv('AWS_REGION')}")
    except Exception as e:
        logger.error(f"Failed to initialize AWS SES client: {str(e)}")
        raise

    # OTP Email
    if options.otp:
        logger.info("Processing OTP email request")
        try:
            otp_code = context.otp
            subject = f"ADX Data Portal - OTP - {otp_code}"
            body_html = render_template("otp_mail.html", {"otp": otp_code})
            logger.info(f"OTP email prepared with subject: {subject}")
        except Exception as e:
            logger.error(f"Failed to prepare OTP email: {str(e)}")
            raise

    # Waitlist Email
    elif options.waitlist:
        logger.info("Processing waitlist email request")
        try:
            subject = "ADX Data Portal - Welcome to ADX Data Portal"
            body_html = render_template("waitlist.html", {"data": None})
            logger.info(f"Waitlist email prepared with subject: {subject}")
        except Exception as e:
            logger.error(f"Failed to prepare waitlist email: {str(e)}")
            raise

    # Confirmation Email
    elif options.confirmation:
        logger.info("Processing confirmation email request")
        try:
            dashboard_url = "https://advancex.ai/"
            subject = "ADX Data Portal - Activation Email"
            body_html = render_template("confirmation.html", {"dashboard_url": dashboard_url})
            logger.info(f"Confirmation email prepared with subject: {subject}")
        except Exception as e:
            logger.error(f"Failed to prepare confirmation email: {str(e)}")
            raise

    # Send email without attachment
    if subject and body_html:
        try:
            logger.info(f"Sending email to {recipient} with subject: {subject}")
            response = client.send_email(
                Source=sender_email,
                Destination={'ToAddresses': [recipient]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Html': {'Data': body_html}}
                }
            )
            message_id = response['MessageId']
            logger.info(f"Email sent successfully! Message ID: {message_id}")
            logger.debug(f"Full SES response: {response}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS SES ClientError - Code: {error_code}, Message: {error_message}")
            logger.error(f"Failed to send email to {recipient}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending email to {recipient}: {str(e)}")
            raise

    # T&C Email with Attachment
    if options.tnc:
        logger.info("Processing T&C email with attachment")
        
        try:
            subject = "ADX Data Portal - Terms and Conditions"
            body_html = render_template("tnc.html", {})
            logger.info("T&C email template rendered successfully")

            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = recipient

            msg.attach(MIMEText(body_html, "html"))
            logger.info("T&C email body attached to MIME message")

            attachment_path = context.tnc_location
            logger.info(f"Attempting to attach file: {attachment_path}")
            
            if not os.path.exists(attachment_path):
                logger.error(f"T&C attachment file not found: {attachment_path}")
                raise FileNotFoundError(f"T&C file not found: {attachment_path}")
            
            file_size = os.path.getsize(attachment_path)
            logger.info(f"T&C file size: {file_size} bytes")
            
            with open(attachment_path, "rb") as file:
                part = MIMEApplication(file.read())
                filename = os.path.basename(attachment_path)
                part.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(part)
                logger.info(f"T&C attachment added successfully: {filename}")

        except Exception as e:
            logger.error(f"Failed to prepare T&C email with attachment: {str(e)}")
            return

        try:
            logger.info(f"Sending T&C email with attachment to {recipient}")
            response = client.send_raw_email(
                Source=sender_email,
                Destinations=[recipient],
                RawMessage={"Data": msg.as_string()}
            )
            message_id = response['MessageId']
            logger.info(f"T&C email with attachment sent successfully! Message ID: {message_id}")
            logger.debug(f"Full SES response for T&C email: {response}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS SES ClientError for T&C email - Code: {error_code}, Message: {error_message}")
            logger.error(f"Failed to send T&C email to {recipient}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending T&C email to {recipient}: {str(e)}")
            raise

    logger.info(f"Email send process completed for recipient: {recipient}")

