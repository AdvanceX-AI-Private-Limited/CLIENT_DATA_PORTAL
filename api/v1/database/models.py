from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from ..database.database import Base
from enum import Enum
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

class Client(Base):
    __tablename__ = "clients"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(IST))
    updated_at = Column(DateTime, onupdate=datetime.now(IST))
    last_login = Column(DateTime, onupdate=datetime.now(IST))
    
    # Relationships
    outlets = relationship("Outlet", back_populates="client", cascade="all, delete-orphan")
    users = relationship("User", back_populates="client", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(id={self.id}, username={self.username})>"

class Outlet(Base):
    __tablename__ = "outlets"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    aggregator = Column(String(50), nullable=False)
    resid = Column(String(20), nullable=False)
    subzone = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    outletnumber = Column(String(20), nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.now(IST))
    updated_at = Column(DateTime, onupdate=datetime.now(IST))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="outlets")
    role_mappings = relationship("RoleOutletMapping", back_populates="outlet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Outlet(id={self.id}, outletnumber={self.outletnumber})>"

class User(Base):
    __tablename__ = "users"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    usernumber = Column(String(20), nullable=False)
    useremail = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(IST))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="users")
    role_mappings = relationship("RoleUserMapping", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

class Role(Base):
    __tablename__ = "roles"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    rolename = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(IST))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="roles")
    service_mappings = relationship("RoleServiceMapping", back_populates="role", cascade="all, delete-orphan")
    user_mappings = relationship("RoleUserMapping", back_populates="role", cascade="all, delete-orphan")
    outlet_mappings = relationship("RoleOutletMapping", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Role(id={self.id}, rolename={self.rolename})>"

class Service(Base):
    __tablename__ = "services"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    servicename = Column(String(50), nullable=False)
    servicevariant = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now(IST))
    
    # Relationships
    service_mappings = relationship("RoleServiceMapping", back_populates="service", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Service(id={self.id}, servicename={self.servicename})>"

class RoleServiceMapping(Base):
    __tablename__ = "role_service_mappings"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.now(IST))
    
    # Relationships
    role = relationship("Role", back_populates="service_mappings")
    service = relationship("Service", back_populates="service_mappings")
    client = relationship("Client")

    def __repr__(self):
        return f"<RoleServiceMapping(role_id={self.role_id}, service_id={self.service_id})>"

class RoleUserMapping(Base):
    __tablename__ = "role_user_mappings"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.now(IST))
    
    # Relationships
    role = relationship("Role", back_populates="user_mappings")
    user = relationship("User", back_populates="role_mappings")
    client = relationship("Client")

    def __repr__(self):
        return f"<RoleUserMapping(role_id={self.role_id}, user_id={self.user_id})>"

class RoleOutletMapping(Base):
    __tablename__ = "role_outlet_mappings"
    logger.debug(f"Initializing {__tablename__} table")

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.now(IST))
    
    # Relationships
    role = relationship("Role", back_populates="outlet_mappings")
    outlet = relationship("Outlet", back_populates="role_mappings")
    client = relationship("Client")

    def __repr__(self):
        return f"<RoleOutletMapping(role_id={self.role_id}, outlet_id={self.outlet_id})>"

logger.info("All SQLAlchemy models initialized successfully")