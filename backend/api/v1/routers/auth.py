import base64
from contextlib import contextmanager
import json
import os
import threading
import sqlite3
import pytz
import random
import string
import time
import uuid
import requests
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, Request, Form, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from oauthlib.oauth2 import WebApplicationClient
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional, Tuple
from logger import create_logger
from ..database import models
from ..database.database import get_db
from ..schemas import schemas
from .helpers.send_mail import send_mail

router = APIRouter() 
logger = create_logger(__name__)
env = load_dotenv('.env')

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TNC_FILE_PATH = BASE_DIR / "templates" / "dummy.pdf"

CASHFREE_CLIENT_ID = os.getenv("CASHFREE_CLIENT_ID")
CASHFREE_CLIENT_SECRET = os.getenv("CASHFREE_CLIENT_SECRET")
CASHFREE_VERIFICATION_URL = os.getenv("CASHFREE_VERIFICATION_URL")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
IST = timezone(timedelta(hours=5, minutes=30))
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

#_____________________________ HELPERS _____________________________
class SessionStore:
    def __init__(self, db_path: str = "sessions.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS temp_sessions (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    client_id INTEGER NOT NULL,
                    otp TEXT NOT NULL,
                    otp_timestamp REAL NOT NULL,
                    otp_expiry INTEGER NOT NULL,
                    otp_verified INTEGER DEFAULT 0,
                    session_token TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            ''')
            
            # Create index for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_email_client 
                ON temp_sessions(email, client_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_client_unverified 
                ON temp_sessions(client_id, otp_verified)
            ''')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from the database"""
        current_time = time.time()
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM temp_sessions 
                    WHERE (? - otp_timestamp) > otp_expiry
                ''', (current_time,))
                deleted_count = cursor.rowcount
                conn.commit()
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired sessions")
    
    def store_session(self, session_id: str, session_data: 'SessionData'):
        """Store session data in SQLite"""
        current_time = time.time()
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO temp_sessions 
                    (id, email, client_id, otp, otp_timestamp, otp_expiry, 
                     otp_verified, session_token, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    session_data.email,
                    session_data.client_id,
                    session_data.otp,
                    session_data.otp_timestamp,
                    session_data.otp_expiry,
                    int(session_data.otp_verified),
                    session_data.session_token,
                    current_time,
                    current_time
                ))
                conn.commit()
    
    def get_session(self, session_id: str) -> Optional['SessionData']:
        """Retrieve session data from SQLite"""
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM temp_sessions WHERE id = ?
                ''', (session_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Convert row to SessionData object
                session_data = SessionData(
                    email=row['email'],
                    client_id=row['client_id']
                )
                session_data.otp = row['otp']
                session_data.otp_timestamp = row['otp_timestamp']
                session_data.otp_expiry = row['otp_expiry']
                session_data.otp_verified = bool(row['otp_verified'])
                session_data.session_token = row['session_token']
                
                return session_data
    
    def update_session(self, session_id: str, **updates):
        """Update specific fields of a session"""
        if not updates:
            return
        
        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        set_clauses.append("updated_at = ?")
        values.append(time.time())
        values.append(session_id)
        
        query = f'''
            UPDATE temp_sessions 
            SET {', '.join(set_clauses)}
            WHERE id = ?
        '''
        
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
    
    def delete_session(self, session_id: str):
        """Delete a specific session"""
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM temp_sessions WHERE id = ?', (session_id,))
                conn.commit()
    
    def check_existing_otp(self, email: str, client_id: int) -> Optional[Dict[str, Any]]:
        """Check if there's an active (non-expired) OTP session for the email/client"""
        current_time = time.time()
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, otp_timestamp, otp_expiry, otp_verified 
                    FROM temp_sessions 
                    WHERE email = ? AND client_id = ? AND otp_verified = 0
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (email, client_id))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Check if OTP is still valid
                time_elapsed = current_time - row['otp_timestamp']
                if time_elapsed > row['otp_expiry']:
                    # OTP expired, clean it up
                    cursor.execute('DELETE FROM temp_sessions WHERE id = ?', (row['id'],))
                    conn.commit()
                    return None
                
                return {
                    'session_id': row['id'],
                    'time_remaining': row['otp_expiry'] - time_elapsed,
                    'otp_verified': bool(row['otp_verified'])
                }

class LoginRequest(BaseModel):
    email: str
    password: str

class OTPVerificationRequest(BaseModel):
    token: str
    otp: str
    is_active: bool

class ResendOTPRequest(BaseModel):
    token: str

class GSTINRequest(BaseModel):
    GSTIN: str
    business_name: str

class GSTINResponse(BaseModel):
    success: bool
    data: dict | None = None
    message: str

class LinkedUserResponse(BaseModel):
    message: str
    user: dict

class SessionData:
    def __init__(self, email: str, client_id: int):
        self.email = email
        self.client_id = client_id
        self.otp = self.generate_otp()
        self.otp_timestamp = time.time()
        self.otp_expiry = 300  # 5 minutes
        self.otp_verified = False
        self.session_token = None

        logger.info(f"Session initialized for email: {email}, client_id: {client_id}")
        logger.debug(f"Generated OTP: {self.otp} (expires in {self.otp_expiry} seconds)")
    
    def generate_otp(self) -> str:
        return ''.join(random.choices(string.digits, k=6))
    
    def is_otp_expired(self) -> bool:
        expired = time.time() - self.otp_timestamp > self.otp_expiry
        if expired:
            logger.warning(f"OTP expired for email: {self.email}")
        return expired
    
    def verify_otp(self, submitted_otp: str) -> bool:
        if self.is_otp_expired():
            logger.warning(f"Attempted OTP verification for expired OTP (email: {self.email})")
            return False
        valid = self.otp == submitted_otp
        if valid:
            logger.info(f"OTP verified for email: {self.email}")
        else:
            logger.warning(f"Incorrect OTP submitted for email: {self.email}")
        return valid

def create_session_token_in_db(db: Session, client_id: int, email: str) -> str:
    """Create and store session token in database"""
    session_token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days session

    logger.debug(f"Creating session token for email: {email}, client_id: {client_id}")
    
    # Create new session record in database
    db_session = models.UserSession(
        client_id=client_id,
        session_token=session_token,
        email=email,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        is_active=True
    )

    try:
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        logger.info(f"Session token created and stored for email: {email}")
    except Exception as e:
        logger.error(f"Failed to create session token for email: {email}, error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return session_token

# Helper function to get current session (for use in other routes)
def get_current_session(request: Request, db: Session = Depends(get_db)):
    """
    Dependency to validate session token and get current user
    Usage: current_session = Depends(get_current_session)
    """
    logger.info("Checking current session")
    
    auth_header = request.headers.get("authorization")
    session_token = None
    
    if auth_header and auth_header.startswith("Bearer "):
        session_token = auth_header.split(" ")[1]
        logger.debug("Session token retrieved from authorization header")
    else:
        session_token = request.cookies.get("session_token")
        if session_token:
            logger.debug("Session token retrieved from cookies")
    
    if not session_token:
        logger.warning("No session token provided in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session token provided"
        )
    
    db_session = db.query(models.UserSession).filter(
        models.UserSession.session_token == session_token,
        models.UserSession.is_active == True,
        models.UserSession.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not db_session:
        logger.warning(f"Invalid or expired session token: {session_token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )
    
    logger.info(f"Valid session for user: {db_session.email}")
    return db_session

def check_existing_session(db: Session, client_id: int) -> Tuple[Optional[dict], bool]:
    """
    Check if an active session exists for the client
    
    Returns:
        Tuple[Optional[dict], bool]: 
        - First element: Session data dict if valid session exists, None otherwise
        - Second element: True if session was found but expired (and deleted), False otherwise
    """
    try:
        # Query for existing active session
        existing_session = db.query(models.UserSession).filter(
            models.UserSession.client_id == client_id,
            models.UserSession.is_active == True
        ).first()

        if not existing_session:
            logger.debug(f"No existing session found for client {client_id}")
            return None, False

        # Get current IST time
        ist_tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist_tz)

        # Convert database datetime to IST if it's naive
        if existing_session.expires_at.tzinfo is None:
            expires_at_ist = ist_tz.localize(existing_session.expires_at)
        else:
            expires_at_ist = existing_session.expires_at.astimezone(ist_tz)
            
        if expires_at_ist <= current_time:
            # Session exists but is expired - delete it
            logger.info(f"Found expired session for client {client_id}, deleting...")
            db.delete(existing_session)
            db.commit()
            logger.info(f"Expired session deleted for client {client_id}")
            return None, True
        else:
            # Session exists and is still valid
            logger.info(f"Valid session found for client {client_id}")
            session_data = {
                "session_token": existing_session.session_token,
                "expires_at": expires_at_ist.isoformat(),
                "client_id": existing_session.client_id,
                "email": existing_session.email,
                "created_at": existing_session.created_at.isoformat() if existing_session.created_at else None
            }
            return session_data, False
            
    except Exception as e:
        logger.error(f"Error checking existing session for client {client_id}: {str(e)}")
        db.rollback()
        return None, False

def get_password_hash(password: str):
    return pwd_context.hash(password)

session_store = SessionStore()

#_____________________________ EMAIL LOGIN FLOW _____________________________
@router.post("/login")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint - validates credentials and initiates OTP flow
    Returns: JSON with temp_token for OTP verification or existing session
    """
    logger.info(f"Login attempt for email: {login_data.email}")

    try:
        client = db.query(models.Client).filter(
            models.Client.email == login_data.email 
        ).first()

        if not client:
            logger.warning(f"Login failed: Email not found - {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        is_active = client.is_active

        if not verify_password(login_data.password, client.hashed_password):
            logger.warning(f"Login failed: Incorrect password for email - {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check for existing session using separate function
        session_data, was_expired = check_existing_session(db, client.id)
        
        if session_data:
            # Valid session exists - return it
            logger.info(f"Returning existing valid session for client {client.id}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Already logged in with valid session",
                    "session_token": session_data["session_token"],
                    "expires_at": session_data["expires_at"],
                    "client_id": session_data["client_id"],
                    "user": {
                        "email": session_data["email"],
                        "client_id": session_data["client_id"]
                    },
                    "is_signed_in": True,
                    "is_active": is_active
                }
            )
        
        if was_expired:
            logger.info(f"Expired session was found and deleted for client {client.id}, proceeding with new login")

        # Clean up any expired temporary sessions
        session_store.cleanup_expired_sessions()
        
        # Check if there's already an active OTP session
        existing_otp = session_store.check_existing_otp(login_data.email, client.id)
        
        if existing_otp:
            logger.info(f"Active OTP session found for {login_data.email}, time remaining: {existing_otp['time_remaining']:.0f}s")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": f"OTP already sent. Please check your email or wait {int(existing_otp['time_remaining'])} seconds to request a new one.",
                    "temp_token": existing_otp['session_id'],
                    "expires_in": int(existing_otp['time_remaining']),
                    "next_step": "verify_otp",
                    "is_signed_in": False,
                    "otp_already_sent": True,
                    "is_active": is_active
                }
            )

        # No valid session exists and no active OTP, proceed with new OTP flow
        # Create session data with OTP
        temp_session_id = str(uuid.uuid4())
        session_data = SessionData(email=login_data.email, client_id=client.id)
        
        # Store in SQLite instead of memory
        session_store.store_session(temp_session_id, session_data)

        logger.info(f"Temporary session created for email: {login_data.email}, session_id: {temp_session_id}")

        # Send OTP via email
        try:
            mail_payload = {
                "recipient_email": login_data.email,
                "mail_options": {
                    "otp": True,
                },
                "mail_context": {
                    "otp": session_data.otp,
                }
            }
            send_mail(data=models.MailRequest(**mail_payload))
            logger.info(f"OTP sent to email: {login_data.email}")
        except Exception as mail_error:
            logger.error(f"Failed to send OTP email to {login_data.email}: {mail_error}")
            # Clean up session if email fails
            session_store.delete_session(temp_session_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP email"
            )

        logger.debug(f"Login flow complete for {login_data.email}, returning temp_token")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Login successful. OTP sent to your email.",
                "temp_token": temp_session_id,
                "expires_in": 300,  # 5 minutes
                "next_step": "verify_otp",
                "is_signed_in": False,
                "otp_already_sent": False,
                "is_active": is_active
            }
        )

    except HTTPException as http_exc:
        logger.warning(f"HTTPException during login for {login_data.email}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during login for {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/verify-otp")
async def verify_otp_route(otp_data: OTPVerificationRequest, db: Session = Depends(get_db)):
    """
    OTP verification endpoint
    Returns: JSON with session_token on success
    """
    logger.info(f"OTP verification attempt with token: {otp_data.token}")

    try:
        session_data = session_store.get_session(otp_data.token)

        if not session_data:
            logger.warning(f"Invalid or expired temp token: {otp_data.token}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired temporary token"
            )

        # Check if OTP is expired
        if session_data.is_otp_expired():
            logger.warning(f"Expired OTP for token: {otp_data.token}, email: {session_data.email}")
            # Clean up expired session from SQLite
            session_store.delete_session(otp_data.token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OTP has expired. Please login again."
            )

        # Verify OTP
        if not session_data.verify_otp(otp_data.otp):
            logger.warning(f"Invalid OTP for email: {session_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )

        # Mark OTP as verified in SQLite
        session_store.update_session(otp_data.token, otp_verified=1)
        logger.info(f"OTP verified for email: {session_data.email}")

        try:
            # Create permanent session token in database
            db_session_token = create_session_token_in_db(
                db=db,
                client_id=session_data.client_id,
                email=session_data.email
            )

            logger.info(f"Session token created for email: {session_data.email}")

            # Clean up temporary session from SQLite after successful verification
            session_store.delete_session(otp_data.token)
            logger.debug(f"Temporary session deleted for token: {otp_data.token}")

            # Fetch the session from the DB to get the expires_at value
            db_session = db.query(models.UserSession).filter(
                models.UserSession.session_token == db_session_token
            ).first()

            expires_at = db_session.expires_at.isoformat() if db_session and db_session.expires_at else None

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "OTP verified successfully",
                    "session_token": db_session_token,
                    "expires_at": expires_at,
                    "user": {
                        "email": session_data.email,
                        "client_id": session_data.client_id
                    },
                    "is_active": otp_data.is_active
                }
            )

        except Exception as e:
            logger.error(f"Failed to create session token for email: {session_data.email} - {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create session"
            )

    except HTTPException as http_exc:
        logger.warning(f"HTTPException during OTP verification for token {otp_data.token}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during OTP verification for token {otp_data.token}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during OTP verification"
        )

# Cleanup function that can be called periodically
def cleanup_expired_temp_sessions():
    """Function to clean up expired temporary sessions - can be called by a scheduler"""
    session_store.cleanup_expired_sessions()

@router.post("/resend-otp")
async def resend_otp(resend_data: ResendOTPRequest):
    """
    Resend OTP endpoint
    Returns: JSON confirmation
    """
    logger.info(f"Resend OTP request received for token: {resend_data.token}")

    try:
        session_data = session_store.get(resend_data.token)
        if not session_data:
            logger.warning(f"Invalid or expired temp token for resend: {resend_data.token}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired temporary token"
            )

        # Generate new OTP
        session_data.otp = session_data.generate_otp()
        session_data.otp_timestamp = time.time()
        logger.info(f"New OTP generated for email: {session_data.email}")

        # Send new OTP
        try:
            mail_payload = {
                "recipient_email": session_data.email,
                "mail_options": {
                    "otp": True,
                },
                "mail_context": {
                    "otp": session_data.otp,
                }
            }
            send_mail(data=models.MailRequest(**mail_payload))
            logger.info(f"OTP resent successfully to {session_data.email}")
        except Exception as mail_error:
            logger.error(f"Failed to resend OTP email to {session_data.email}: {mail_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP email"
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "New OTP sent to your email",
                "expires_in": 300  # 5 minutes
            }
        )

    except HTTPException as http_exc:
        logger.warning(f"HTTPException during resend OTP for token {resend_data.token}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error while resending OTP for token: {resend_data.token}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while resending OTP"
        )

@router.post("/new-registration")
async def new_registration(
    registration_data: schemas.NewRegistration,
    current_session = Depends(get_current_session), 
    db: Session = Depends(get_db)):
    
    logger.info(f"Login attempt for registration")

    try:
        # Check if brand and client exists
        brand_exists = db.query(models.Brand).filter(
            models.Brand.id == registration_data.brand_id
            ).first()
        if not brand_exists:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid brand id passed - {registration_data.brand_id}"
            )

        client_exists = db.query(models.Client).filter(
            models.Client.id == registration_data.client_id
            ).first()
        if not client_exists:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid client id passed - {registration_data.client_id}"
            )
        
        if brand_exists and client_exists:
            try:
                db_registration = models.NewRegistration(
                    client_id=registration_data.client_id,
                    brand_id=registration_data.brand_id,
                    tnc_status=registration_data.tnc_status,
                    tnc_accepted_at=registration_data.tnc_accepted_at,
                    date_of_registration=registration_data.date_of_registration,
                )
                db.add(db_registration)
                db.commit()
                db.refresh(db_registration)
                logger.info(f"New Registration completed for brand_id:{registration_data.brand_id} | client_id:{registration_data.client_id}")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to insert data to database - {e}"
                )
        
        # # Welcome mail + Temp Login Details
        # try:
        #     mail_payload = {
        #         "recipient_email": client_exists.email,
        #         "mail_options": {
        #             "registration": True
        #         },
        #         "mail_context": {
        #             "registation_details": {
        #                 "username": client_exists.username,
        #                 "email": client_exists.email,
        #                 "password": registration_data.client_password
        #             }
        #         }
        #     }
        #     send_mail(data=models.MailRequest(**mail_payload))
        #     logger.info(f"Welcome mail sent: {client_exists.email}")
        # except Exception as mail_error:
        #     logger.error(f"Failed to send OTP email to {client_exists.email}: {mail_error}")
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Failed to send welcome email"
        #     )
        
        # Terms and Conditions
        if "send_on_mail" in registration_data.tnc_status:
            try:
                mail_payload = {
                    "recipient_email": client_exists.email,
                    "mail_options": {
                        "tnc": True
                    },
                    "mail_context": {
                        "tnc_location": TNC_FILE_PATH
                    }
                }
                send_mail(data=models.MailRequest(**mail_payload))
                logger.info(f"TnC mail sent: {client_exists.email}")
            except Exception as mail_error:
                logger.error(f"Failed to send OTP email to {client_exists.email}: {mail_error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send TnC email"
                )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Registation successful. Account is created.",
                "registration_id": db_registration.id 
            }
        )
    
    except HTTPException as http_exc:
        logger.warning(f"HTTPException during registration for {registration_data.brand_id}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during registration for {registration_data.brand_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )
    
@router.get("/send-mail")
async def send_mail_endpoint():
    try:
        if not os.path.exists(TNC_FILE_PATH):
            logger.error(f"T&C attachment file not found: {TNC_FILE_PATH}")
            raise FileNotFoundError(f"T&C file not found: {TNC_FILE_PATH}")

        mail_request_data = {
            "recipient_email": "dontaskrahul@advancex.ai",
            "mail_options": {
                "tnc": True
            },
            "mail_context": {
                "tnc_location": str(TNC_FILE_PATH)
            }
        }

        mail_request = models.MailRequest(**mail_request_data)
        send_mail(mail_request)

        return {"message": "Mail sent successfully"}
    except Exception as e:
        logger.exception("Error sending mail")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/terms")
def download_terms():
    try:
        s3_url = "https://adx-backend.s3.ap-south-1.amazonaws.com/PUBLIC/DOCUMENTS/dummy.pdf"
        file = requests.get(s3_url)
        return Response(
            content=file.content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="Terms_and_Conditions.pdf"'
            }
        )
    
    except HTTPException as http_exc:
        logger.warning(f"HTTPException during Google login: {http_exc}")
        raise
    except Exception as e:
        logger.exception("Unexpected error during Google login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    """
    Logout endpoint - invalidates session token
    Returns: JSON confirmation
    """
    print("Cookies: ", request.cookies.get("session_token"))
    try:
        logger.info("Logout request received")

        # Get session token from authorization header or request body
        auth_header = request.headers.get("authorization")
        session_token = None
        print(request.headers.get("authorization"))
        
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
            logger.debug("Session token retrieved from authorization header")
        else:
            session_token = request.cookies.get("session_token")
            if session_token:
                logger.debug("Session token retrieved from cookies")
        
        if not session_token:
            logger.warning("No session token provided in request")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No session token provided"
            )
        
        # Invalidate session in database
        logger.info(f"Attempting to invalidate session token: {session_token}")
        db_session = db.query(models.UserSession).filter(
            models.UserSession.session_token == session_token,
            models.UserSession.is_active == True
        ).first()
        
        if db_session:
            db_session.is_active = False
            db.commit()
            logger.info(f"Session token {session_token} successfully invalidated")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Logged out successfully"
                }
            )
        else:
            logger.warning(f"Invalid or expired session token: {session_token}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token"
            )
            
    except HTTPException as e:
        logger.error(f"HTTPException during logout: {e.detail}")
        raise
    except Exception as e:
        logger.exception("Unhandled exception during logout")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )

# Example protected route
@router.post("/protected/profile")
async def get_profile(
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    """
    Example protected route that requires valid session
    """
    logger.info(f"Fetching profile for client_id: {current_session.client_id}")
    
    client = db.query(models.Client).filter(
        models.Client.id == current_session.client_id
    ).first()
    
    if client:
        logger.info(f"Profile successfully retrieved for user: {current_session.email}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Profile retrieved successfully",
                "profile": {
                    "email": current_session.email,
                    "client_id": current_session.client_id,
                    # Add other profile fields as needed
                }
            }
        )
    else:
        logger.warning(f"Client not found for client_id: {current_session.client_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )


#_____________________________ GOOGLE LOGIN FLOW _____________________________
# Configure Google O2 Auth
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Remove this in production
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL")
FRONTEND_LOGIN_SUCCESS_PATH = "/auth/callback/success"
FRONTEND_LOGIN_ERROR_PATH = "/auth/callback/error"

DATA = {
    'response_type': "code",
    'redirect_uri': GOOGLE_REDIRECT_URI,
    'scope': 'https://www.googleapis.com/auth/userinfo.email',
    'client_id': GOOGLE_CLIENT_ID,
    'prompt': 'consent'
}
URL_DICT = {
    'google_oauth': 'https://accounts.google.com/o/oauth2/v2/auth',
    'token_gen': 'https://oauth2.googleapis.com/token',
    'get_user_info': 'https://www.googleapis.com/oauth2/v3/userinfo'
}
GOOGLE_CLIENT = WebApplicationClient(GOOGLE_CLIENT_ID)

import urllib.parse
from fastapi import HTTPException, status, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import json
import base64

FRONTEND_LOGIN_SUCCESS_PATH = "/auth/callback/success"
FRONTEND_LOGIN_ERROR_PATH = "/auth/callback/error"

def encode_response_data(data: dict) -> str:
    """Encode response data to be safely passed in URL parameters"""
    json_str = json.dumps(data)
    encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
    return encoded

def create_frontend_redirect_url(success: bool, data: dict) -> str:
    """Create the frontend redirect URL with encoded data"""
    if success:
        path = FRONTEND_LOGIN_SUCCESS_PATH
    else:
        path = FRONTEND_LOGIN_ERROR_PATH
    
    encoded_data = encode_response_data(data)
    return f"{FRONTEND_BASE_URL}{path}?data={encoded_data}"

@router.get('/google/login')
async def google_login():
    """Redirect to Google Sign-In page."""
    logger.info('Initiating login flow, redirecting to Google sign-in page.')

    try:
        req_uri = GOOGLE_CLIENT.prepare_request_uri(
            uri=URL_DICT['google_oauth'],
            redirect_uri=DATA['redirect_uri'],
            scope=DATA['scope'],
            prompt=DATA['prompt']
        )
        logger.info(f'Request URI prepared: {req_uri}')
        return RedirectResponse(url=req_uri)

    except HTTPException as http_exc:
        logger.warning(f"HTTPException during Google login: {http_exc}")
        # Redirect to frontend with error
        error_data = {
            "error": "oauth_init_failed",
            "message": "Failed to initialize Google OAuth",
            "details": str(http_exc.detail) if hasattr(http_exc, 'detail') else str(http_exc)
        }
        redirect_url = create_frontend_redirect_url(success=False, data=error_data)
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        logger.exception("Unexpected error during Google login")
        error_data = {
            "error": "internal_error",
            "message": "Internal server error during login initialization"
        }
        redirect_url = create_frontend_redirect_url(success=False, data=error_data)
        return RedirectResponse(url=redirect_url)

@router.get('/google/callback')
async def callback(code: str, fastapi_request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth2 callback and redirect to frontend with results."""
    logger.info('Google OAuth2 callback received.')
    logger.info(f'Received code: {code}')

    try:
        # Token exchange
        token_url, headers, body = GOOGLE_CLIENT.prepare_token_request(
            URL_DICT['token_gen'],
            authorization_response=str(fastapi_request.url),
            redirect_url=DATA['redirect_uri'],
            code=code
        )
        logger.info(f'Token request prepared. URL: {token_url}')
        logger.debug(f'Token headers: {headers}')
        logger.debug(f'Token body: {body}')

        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        )

        logger.info(f'Token response status: {token_response.status_code}')
        logger.debug(f'Token response body: {token_response.text}')

        if not token_response.ok:
            logger.error(f'Token request failed: {token_response.text}')
            error_data = {
                "error": "token_exchange_failed",
                "message": "Failed to retrieve token from Google",
                "details": token_response.text
            }
            redirect_url = create_frontend_redirect_url(success=False, data=error_data)
            return RedirectResponse(url=redirect_url)

        GOOGLE_CLIENT.parse_request_body_response(token_response.text)

    except Exception as e:
        logger.exception("Token exchange failed")
        error_data = {
            "error": "token_exchange_failed",
            "message": "OAuth token exchange failed",
            "details": str(e)
        }
        redirect_url = create_frontend_redirect_url(success=False, data=error_data)
        return RedirectResponse(url=redirect_url)

    try:
        # Get user info from Google
        uri, headers, body = GOOGLE_CLIENT.add_token(URL_DICT['get_user_info'])
        user_info_resp = requests.get(uri, headers=headers, data=body)
        user_info = user_info_resp.json()

        logger.info(f'User info obtained: {user_info}')
    except Exception as e:
        logger.exception("Failed to fetch user info")
        error_data = {
            "error": "user_info_failed",
            "message": "Failed to retrieve user info from Google",
            "details": str(e)
        }
        redirect_url = create_frontend_redirect_url(success=False, data=error_data)
        return RedirectResponse(url=redirect_url)

    user_email = user_info.get('email')
    if not user_email:
        error_data = {
            "error": "no_email",
            "message": "Email not found in Google account"
        }
        redirect_url = create_frontend_redirect_url(success=False, data=error_data)
        return RedirectResponse(url=redirect_url)

    # ______________________ LOGGED IN VIA GOOGLE __________________________
    # Now we will check if google is linked with any account
    # If yes -> Is session present -> Is expired -> Yes -> Create New
    #                                            -> No -> Return Existing
    # If no -> Return HTTP_403_FORBIDDEN

    try:
        client = db.query(models.Client).filter(
            models.Client.email == user_email
        ).first()

        if not client:
            logger.warning(f"Login failed: No account for {user_email}")
            error_data = {
                "error": "account_not_found",
                "message": "Account not found. Please sign up first.",
                "email": user_email,
                "action_required": "signup"
            }
            redirect_url = create_frontend_redirect_url(success=False, data=error_data)
            return RedirectResponse(url=redirect_url)

        # Check for existing session first
        session_data, was_expired = check_existing_session(db, client.id)
        
        if was_expired:
            logger.info(f"Expired session was found and deleted for client {client.id}")

        if not client.google_linked:
            # Google is not linked - redirect with error
            logger.info(f"Account found but Google not linked for {user_email}")
            
            error_data = {
                "error": "google_not_linked",
                "message": "Google account is not connected to this user. Please link your Google account.",
                "email": user_email,
                "user": {
                    "client_id": client.id,
                    "name": client.username,
                    "email": client.email
                },
                "action_required": "link_google"
            }
            
            # If valid session exists, include it in response
            if session_data:
                logger.info(f"Valid session exists for client {client.id} but Google not linked")
                error_data.update({
                    "session_token": session_data["session_token"],
                    "expires_at": session_data["expires_at"],
                    "session_status": "valid_session_exists"
                })
            else:
                error_data["session_status"] = "no_valid_session"
            
            redirect_url = create_frontend_redirect_url(success=False, data=error_data)
            return RedirectResponse(url=redirect_url)

        # Google is linked - check session and proceed accordingly
        if session_data:
            # Valid session exists - redirect with success
            logger.info(f"Valid session exists for Google-linked client {client.id}")
            success_data = {
                "message": "Login successful. Existing session found.",
                "session_token": session_data["session_token"],
                "expires_at": session_data["expires_at"],
                "expires_in": 7 * 24 * 60 * 60,  # 7 days in seconds
                "user": {
                    "email": client.email,
                    "client_id": client.id,
                    "name": client.username
                },
                "session_status": "existing_session",
                "login_method": "google_oauth"
            }
            redirect_url = create_frontend_redirect_url(success=True, data=success_data)
            return RedirectResponse(url=redirect_url)
        else:
            # No valid session exists - create new session and redirect with success
            logger.info(f"No valid session found for Google-linked client {client.id}, creating new session")
            session_token = create_session_token_in_db(
                db=db,
                client_id=client.id,
                email=client.email
            )
            logger.info(f"New session token created for {user_email}")

            # Get the created session to include expires_at
            db_session = db.query(models.UserSession).filter(
                models.UserSession.session_token == session_token
            ).first()
            
            expires_at = db_session.expires_at.isoformat() if db_session and db_session.expires_at else None

            success_data = {
                "message": "Login successful. New session created.",
                "session_token": session_token,
                "expires_at": expires_at,
                "expires_in": 7 * 24 * 60 * 60,  # 7 days in seconds
                "user": {
                    "email": client.email,
                    "client_id": client.id,
                    "name": client.username
                },
                "session_status": "new_session_created",
                "login_method": "google_oauth"
            }
            redirect_url = create_frontend_redirect_url(success=True, data=success_data)
            return RedirectResponse(url=redirect_url)

    except Exception as e:
        logger.exception("Error during account lookup or session creation")
        db.rollback()
        error_data = {
            "error": "internal_error",
            "message": "Internal server error during login",
            "details": str(e)
        }
        redirect_url = create_frontend_redirect_url(success=False, data=error_data)
        return RedirectResponse(url=redirect_url)

@router.post("/google/link", response_model=LinkedUserResponse)
async def link_google_account(
    request: Request,
    db: Session = Depends(get_db),
    current_session = Depends(get_current_session)
):
    """
    Link the current user's account with Google (set google_linked = True).
    Requires the user to be logged in with a valid session.
    """
    try:
        print(current_session)
        user_email = current_session.email
        logger.info(f"Attempting to link Google for: {user_email}")

        client = db.query(models.Client).filter(models.Client.email == user_email).first()

        if not client:
            logger.warning(f"Client not found for email: {user_email}")
            raise HTTPException(status_code=404, detail="Client not found")

        if client.google_linked:
            logger.info(f"Google already linked for: {user_email}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Google account is already linked",
                    "user": {
                        "client_id": client.id,
                        "email": client.email
                    }
                }
            )

        client.google_linked = True
        db.commit()
        logger.info(f"Google successfully linked for: {user_email}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Google account successfully linked",
                "user": {
                    "client_id": client.id,
                    "email": client.email
                }
            }
        )

    except Exception as e:
        logger.exception("Failed to link Google account")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to link Google account")


#_____________________________ REGISTER LOGIN FLOW _____________________________
@router.post("/clients/register/", response_model=schemas.DisplayClient, status_code=status.HTTP_201_CREATED)
async def register_client(
    client: schemas.ClientCreate, 
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt for Client Registation - {client.email}")

    try:
        # Check if email already exists
        db_client = db.query(models.Client).filter(
            (models.Client.email == client.email)
        ).first()
        if db_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        try:
            hashed_password = get_password_hash(client.password.get_secret_value())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get password hash - {e}"
            )
        
        access_type = client.accesstype
        if "@advancex.ai" in client.email:
            access_type = "internal"
        else:
            access_type = client.accesstype
        
        try:
            db_client = models.Client(
                username=client.username,
                email=client.email,
                hashed_password=hashed_password,
                accesstype=access_type,
                is_active=client.is_active,
                google_linked=client.google_linked
            )
            db.add(db_client)
            db.commit()
            db.refresh(db_client)
            logger.info(f"New Client created successfully")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Registation successful. Account is created.",
                    "client_id": db_client.id 
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to insert data to database - {e}"
            )
        
    except HTTPException as http_exc:
        logger.warning(f"HTTPException during registration for {client.email}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during registration for {client.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/verify-gstin", response_model=GSTINResponse, status_code=status.HTTP_200_OK)
async def verify_gstin(payload: GSTINRequest):

    logger.info(f"Verify gst attempt for  - {payload.business_name}")

    try:
        headers = {
            "x-client-id": CASHFREE_CLIENT_ID,
            "x-client-secret": CASHFREE_CLIENT_SECRET,
            "Content-Type": "application/json"
        }

        response = requests.post(CASHFREE_VERIFICATION_URL, json=payload.model_dump(), headers=headers)

        try:
            response_data = response.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response from Cashfree API"
            )

        if response.status_code == 200:
            return GSTINResponse(
                success=True,
                data=response_data,
                message="GSTIN verified successfully"
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response_data.get("message", "Failed to verify GSTIN")
            )
    
    except HTTPException as http_exc:
        logger.warning(f"HTTPException during registration for {payload.business_name}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during registration for {payload.business_name}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/brands/register/", response_model=schemas.DisplayBrand, status_code=status.HTTP_201_CREATED)
async def register_brand(
    brand: schemas.BrandCreate, 
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt for Brand Registation - {brand.brandname}")
    
    try:
        # Check if brand/gstin already exists
        existing_by_gst = db.query(models.Brand).filter(
            models.Brand.gstin == brand.gstin
            ).first()
        if existing_by_gst:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A brand with this GSTIN already exists."
            )
        
        # Check for existing brand under same client
        existing_by_client = db.query(models.Brand).filter(
            models.Brand.client_id == brand.client_id
            ).first()
        if existing_by_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This client already has a brand registered."
            )
        
        try:
            db_brand = models.Brand(
                brandname=brand.brandname,
                gstin=brand.gstin,
                legal_name_of_business=brand.legal_name_of_business,
                date_of_registration=brand.date_of_registration,
                gstdoc=brand.gstdoc,
                client_id=brand.client_id,
            )
            db.add(db_brand)
            db.commit()
            db.refresh(db_brand)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Registration successful. Brand is created.",
                    "brand_id": db_brand.id
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to insert data to database - {e}"
            )
    
    except HTTPException as http_exc:
        logger.warning(f"HTTPException during registration for {brand.brandname}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during registration for {brand.brandname}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.get("/user/is-active")
async def get_user_is_active(
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    """
    Returns the is_active status of the current user.
    """
    logger.info(f"Checking is_active for client_id: {current_session.client_id}")

    client = db.query(models.Client).filter(
        models.Client.id == current_session.client_id
    ).first()

    if client:
        logger.info(f"is_active for user {client.email}: {client.is_active}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "is_active": client.is_active
            }
        )
    else:
        logger.warning(f"Client not found for client_id: {current_session.client_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )