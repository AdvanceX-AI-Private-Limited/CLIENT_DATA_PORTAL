from typing import Optional
from sqlalchemy import (
    JSON,
    Column,
    Date,
    Integer,
    String,
    ForeignKey,
    Boolean,
    DateTime,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from ..database.database import Base
from enum import Enum
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from logger import create_logger

# Initialize logger
logger = create_logger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))
logger.info(f"Timezone set to IST: {IST}")

class StatusEnum(str, Enum):
    """Enum for status options"""
    active = "Active"
    inactive = "Inactive"
    all = "All"

class MailOptions(BaseModel):
    otp: bool = False
    tnc: bool = False
    registration: bool = False
    waitlist: bool = False
    confirmation: bool = False
    invoice: bool = False

class RegistrationDetails(BaseModel):
    username: str
    mail: str
    password: str

class MailContext(BaseModel):
    otp: Optional[int] = None
    tnc_location: Optional[str] = None
    registation_details: Optional[RegistrationDetails] = None
    invoice_location: Optional[str] = None

class MailRequest(BaseModel):
    recipient_email: str
    mail_options: MailOptions
    mail_context: MailContext

class UserSession(Base):
    __tablename__ = "user_sessions"
    logger.debug(f"Initializing {__tablename__} table")
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship with Client model
    client = relationship("Client", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(id={self.id}, email={self.email})>"


class Client(Base):
    __tablename__ = "clients"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    accesstype = Column(String(50), nullable=False)
    google_linked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(IST))
    
    # Relationships
    outlets = relationship("Outlet", back_populates="client", cascade="all, delete-orphan")
    users = relationship("User", back_populates="client", cascade="all, delete-orphan")
    brands = relationship("Brand", back_populates="client", cascade="all, delete-orphan")
    outlet_services = relationship("OutletService", back_populates="client", cascade="all, delete-orphan")
    user_services = relationship("UserService", back_populates="client", cascade="all, delete-orphan")
    user_outlets = relationship("UserOutlet", back_populates="client", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="client", cascade="all, delete-orphan")
    registrations = relationship("NewRegistration", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(id={self.id}, username={self.username})>"


class Brand(Base):
    __tablename__ = "brands"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    brandname = Column(String(255), unique=True, index=True, nullable=False)
    contact_number = Column(Integer, nullable=True)
    contact_email = Column(String(255), nullable=True)
    gstin = Column(String(15), unique=True, nullable=False)
    legal_name_of_business = Column(String(255), nullable=False)
    date_of_registration = Column(Date, nullable=False)
    gstdoc = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(IST))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    # Relationships
    client = relationship("Client", back_populates="brands")
    outlets = relationship("Outlet", back_populates="brand", cascade="all, delete-orphan")
    registration = relationship("NewRegistration", back_populates="brand", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Brand(id={self.id}, brandname={self.brandname})>"


class NewRegistration(Base):
    __tablename__ = "new_registration"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    tnc_status = Column(String(255), nullable=False)
    tnc_accepted_at = Column(DateTime, default=lambda: datetime.now(IST))
    date_of_registration = Column(DateTime, default=lambda: datetime.now(IST))
    date_of_acceptance = Column(DateTime, nullable=True)

    # Relationships
    client = relationship("Client", back_populates="registrations")
    brand = relationship("Brand", back_populates="registration")

    def __repr__(self):
        return f"<Registration(id={self.id}, brand_id={self.brand_id})>"


class Outlet(Base):
    __tablename__ = "outlets"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    aggregator = Column(String(50), nullable=False)
    resid = Column(String(20), nullable=False)
    subzone = Column(String(50), nullable=False)
    resshortcode = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    outletnumber = Column(String(20), nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.now(IST))
    updated_at = Column(DateTime, onupdate=datetime.now(IST))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)

    __table_args__ = (UniqueConstraint('aggregator', 'resid', name='uq_aggregator_resid'),)

    # Relationships
    client = relationship("Client", back_populates="outlets")
    brand = relationship("Brand", back_populates="outlets")
    outlet_services = relationship("OutletService", back_populates="outlet", cascade="all, delete-orphan")
    user_outlets = relationship("UserOutlet", back_populates="outlet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Outlet(id={self.id}, outletnumber={self.outletnumber})>"


class User(Base):
    __tablename__ = "users"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    usernumber = Column(String(20), unique=True, index=True, nullable=False)  # Changed to String
    useremail = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(IST))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    __table_args__ = (UniqueConstraint('usernumber', 'useremail', name='uq_number_email'),)

    # Relationships
    client = relationship("Client", back_populates="users")
    user_services = relationship("UserService", back_populates="user", cascade="all, delete-orphan")
    user_outlets = relationship("UserOutlet", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
    

class Service(Base):
    __tablename__ = "services"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    servicename = Column(String(50), nullable=False)
    servicevariant = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now(IST))

    # Relationships
    outlet_services = relationship("OutletService", back_populates="service", cascade="all, delete-orphan")
    user_services = relationship("UserService", back_populates="service", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Service(id={self.id}, servicename={self.servicename})>"


class OutletService(Base):
    __tablename__ = "outlet_services"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False) 
    created_at = Column(DateTime, default=datetime.now(IST))

    __table_args__ = (UniqueConstraint('outlet_id', 'service_id', name='uq_outlet_service'),)

    # Relationships
    client = relationship("Client", back_populates="outlet_services")
    outlet = relationship("Outlet", back_populates="outlet_services")
    service = relationship("Service", back_populates="outlet_services")

    def __repr__(self):
        return f"<OutletService(outlet_id={self.outlet_id}, service_id={self.service_id})>"


class UserService(Base):
    __tablename__ = "user_services"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False) 
    created_at = Column(DateTime, default=datetime.now(IST))

    __table_args__ = (UniqueConstraint('user_id', 'service_id', name='uq_user_service'),)

    # Relationships
    client = relationship("Client", back_populates="user_services")
    user = relationship("User", back_populates="user_services")
    service = relationship("Service", back_populates="user_services")

    def __repr__(self):
        return f"<UserService(user_id={self.user_id}, service_id={self.service_id})>"


class UserOutlet(Base):
    __tablename__ = "user_outlets"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    outlet_id = Column(Integer, ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False) 
    created_at = Column(DateTime, default=datetime.now(IST))

    __table_args__ = (UniqueConstraint('user_id', 'outlet_id', name='uq_user_outlet'),)

    # Relationships
    client = relationship("Client", back_populates="user_outlets")
    user = relationship("User", back_populates="user_outlets")
    outlet = relationship("Outlet", back_populates="user_outlets")

    def __repr__(self):
        return f"<UserOutlet(user_id={self.user_id}, outlet_id={self.outlet_id})>"


logger.info("All SQLAlchemy models initialized successfully")