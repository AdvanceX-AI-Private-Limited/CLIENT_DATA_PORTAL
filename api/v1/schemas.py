from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr, Field, constr, field_validator
from typing import Optional, List
from datetime import datetime

class DisplayBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# ============== CORE ENTITIES ==============

# ______________ CLIENTS ____________________
class ClientBase(BaseModel):
    username: str = Field(
        ..., 
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        examples=["user_123"],
        description="Unique username (alphanumeric + underscore)",
        json_schema_extra={"pattern_error": "Only letters, numbers and underscores allowed"}
    )
    email: EmailStr = Field(
        ...,
        examples=["user@example.com"],
        description="Verified email address"
    )

class ClientCreate(ClientBase):
    password: SecretStr = Field(
        ...,
        min_length=8,
        examples=["Str0ngP@ss"],
        description="Must contain 8+ chars with mix of letters, numbers, and symbols",
        # pattern=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
    )

class DisplayClient(DisplayBase, ClientBase):
    id: int = Field(..., examples=[1])
    username: str
    email: EmailStr
    is_active: bool = Field(default=None, description="Account active status")
    created_at: datetime

    def __str__(self):
        return f"Client {self.username} ({self.email})"

class ClientInDB(DisplayClient):
    hashed_password: str
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

# ______________ OUTLETS ____________________
class OutletBase(BaseModel):
    aggregator: str = Field(
        ...,
        min_length=2,
        max_length=50,
        examples=["Zomato / Swiggy"],
        description="Delivery platform name"
    )
    resid: str = Field(
        ...,
        pattern=r'^\d+$',
        min_length=3,
        max_length=20,
        examples=["12345"],
        description="Aggregator's numeric restaurant ID"
    )
    subzone: str = Field(
        ...,
        min_length=2,
        max_length=50,
        examples=["Pali Hill / Koramangala"],
        description="Neighborhood/district"
    )
    city: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[A-Za-z\s]+$",
        examples=["Mumbai / Delhi"],
        description="City name (letters only)"
    )
    outletnumber: str = Field(
        ...,
        pattern=r'^\d+$',
        min_length=3,
        max_length=30,
        examples=["123456"],
        description="Internal numeric outlet ID (digits only)"
    )
    is_active: bool = Field(
        default=True,
        examples=[True],
        description="Whether the Outlet is active/open"
    )

class OutletCreate(OutletBase):
    clientid: int = Field(
        ...,
        gt=0,
        examples=[1],
        description="Owning client ID"
    )

class DisplayOutlet(DisplayBase):
    id: int
    aggregator: str
    resid: str
    subzone: str
    city: str
    outletnumber: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    client: DisplayClient

    def __str__(self):
        return f"Outlet {self.outletnumber} ({self.aggregator})"

# ______________ USERS ____________________
class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        examples=["Rahul Singh"],
        description="User's login name"
    )
    usernumber: int = Field(
        ...,
        pattern=r'^\d+$',
        examples=["1234567891"],
        description="Phone number without country code"
    )
    useremail: EmailStr = Field(
        ...,
        examples=["user@example.com"],
        description="User's primary email"
    )

class UserCreate(UserBase):
    clientid: int = Field(
        ...,
        gt=0,
        examples=[1],
        alias="clientid",
        description="Associated client ID"
    )

class DisplayUser(DisplayBase):
    id: int
    username: str
    usernumber: str
    useremail: EmailStr
    is_active: bool
    created_at: datetime
    client: DisplayClient

    def __str__(self):
        return f"User {self.username} ({self.useremail})"

# ______________ ROLES ____________________
class RoleBase(BaseModel):
    rolename: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-z_]+$",
        examples=["manager", "area_manager"],
        description="Lowercase role identifier with underscores"
    )

class RoleCreate(RoleBase):
    clientid: int = Field(
        ...,
        gt=0,
        examples=[1],
        alias="clientid",
        description="Client who owns this role"
    )

class DisplayRole(DisplayBase):
    id: int
    rolename: str
    created_at: datetime
    client: DisplayClient

    def __str__(self):
        return f"Role {self.rolename.title().replace('_', ' ')}"

# ______________ SERVICES ____________________
class ServiceBase(BaseModel):
    servicename: str = Field(
        ...,
        min_length=3,
        max_length=50,
        examples=["delivery", "pickup"],
        description="Primary service name"
    )
    servicevariant: str = Field(
        ...,
        min_length=2,
        max_length=50,
        examples=["standard", "express"],
        description="Service type variation"
    )

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    id: int
    servicename: str
    servicevariant: str

class DisplayService(DisplayBase):
    id: int
    servicename: str
    servicevariant: str
    created_at: datetime

    def __str__(self):
        return f"{self.servicename.title()} ({self.servicevariant})"

# ============== MAPPING TABLES ==============

# ______________ ROLE-SERVICE MAPPING ____________________
class RoleServiceMappingCreate(BaseModel):
    roleid: int = Field(..., gt=0, examples=[1])
    serviceid: int = Field(..., gt=0, examples=[1])
    clientid: int = Field(..., gt=0, examples=[1])

class DisplayRoleServiceMapping(DisplayBase):
    id: int
    role: DisplayRole
    service: DisplayService
    client: DisplayClient
    assigned_at: datetime

# ______________ ROLE-USER MAPPING ____________________
class RoleUserMappingCreate(BaseModel):
    roleid: int = Field(..., gt=0, examples=[1])
    userid: int = Field(..., gt=0, examples=[1])
    clientid: int = Field(..., gt=0, examples=[1])

class DisplayRoleUserMapping(DisplayBase):
    id: int
    role: DisplayRole
    user: DisplayUser
    client: DisplayClient
    assigned_at: datetime

# ______________ ROLE-OUTLET MAPPING ____________________
class RoleOutletMappingCreate(BaseModel):
    roleid: int = Field(..., gt=0, examples=[1])
    outletid: int = Field(..., gt=0, examples=[1])
    clientid: int = Field(..., gt=0, examples=[1])

class DisplayRoleOutletMapping(DisplayBase):
    id: int
    role: DisplayRole
    outlet: DisplayOutlet
    client: DisplayClient
    assigned_at: datetime
