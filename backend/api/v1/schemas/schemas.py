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
        description="alphanumeric + underscore",
        json_schema_extra={"pattern_error": "Only letters, numbers and underscores allowed"}
    )
    email: EmailStr = Field(
        ...,
        examples=["user@example.com"],
        description="Verified email address"
    )
    accesstype: str = Field(
        default="client",
        description="Access type of the client. Default is 'client'.",
        example="client",
        max_length=50
    )
    is_active: Optional[bool] = Field(
        default=True,
        description="Whether the client is currently active.",
        example=True
    )

class ClientCreate(ClientBase):
    password: SecretStr = Field(
        ...,
        min_length=5,
        max_length=30,
        examples=["Str0ngP@ss"],
        description="Must contain 8+ chars with mix of letters, numbers, and symbols",
        # pattern=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
    )

class DisplayClient(DisplayBase, ClientBase):
    id: int = Field(..., examples=[1])
    created_at: datetime
    updated_at: Optional[datetime] = None

    def __str__(self):
        return f"Client {self.username} ({self.email})"

class ClientInDB(DisplayClient):
    hashed_password: str

# ______________ BRANDS ____________________
class BrandBase(BaseModel):
    brandname: str = Field(
        ..., 
        min_length=2,
        max_length=255,
        pattern=r"^[a-zA-Z0-9\s\-_]+$",
        examples=["CoolBrand_2025"],
        description="Name of the brand. Letters, numbers, spaces, dashes and underscores allowed.",
        json_schema_extra={"pattern_error": "Only letters, numbers, spaces, dashes, and underscores allowed"}
    )
    client_id: int = Field(
        ..., 
        description="The ID of the client this brand belongs to.", 
        examples=[1]
    )

class BrandCreate(BrandBase):
    pass

class DisplayBrand(DisplayBase):
    id: int = Field(..., examples=[10])
    brandname: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    client: DisplayClient

    def __str__(self):
        return f"Brand {self.brandname} (Client ID: {self.client_id})"

class BrandInDB(DisplayBrand):
    pass

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
    brandid: int = Field(
        ...,
        gt=0,
        examples=[1],
        description="Owning brand ID"
    )

class DisplayOutlet(DisplayBase):
    id: int
    aggregator: str
    resid: str
    subzone: str
    resshortcode: str
    city: str
    outletnumber: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    client: DisplayClient
    brand: DisplayBrand

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
    usernumber: int
    useremail: EmailStr
    is_active: bool
    created_at: datetime
    client: DisplayClient

    def __str__(self):
        return f"User {self.username} ({self.useremail})"

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
# ______________ OUTLET <> SERVICE MAPPINGS ____________________
class OutletServiceBase(BaseModel):
    outlet_id: int = Field(
        ..., 
        description="ID of the associated outlet.", 
        examples=[101]
    )
    service_id: int = Field(
        ..., 
        description="ID of the linked service.", 
        examples=[5]
    )

class OutletServiceCreate(OutletServiceBase):
    client_id: int = Field(
        ..., 
        description="The ID of the client this mapping belongs to.", 
        examples=[1]
    )

class DisplayOutletService(DisplayBase):
    id: int
    outlet: DisplayOutlet
    service: DisplayService
    client: DisplayClient
    created_at: datetime

# ______________ USER <> SERVICE MAPPINGS ____________________
class UserServiceBase(BaseModel):
    user_id: int = Field(
        ..., 
        description="ID of the user.",
        examples=[10]
    )
    service_id: int = Field(
        ..., 
        description="ID of the service assigned to the user.", 
        examples=[5]
    )

class UserServiceCreate(UserServiceBase):
    client_id: int = Field(
        ..., 
        description="The ID of the client this mapping belongs to.", 
        examples=[1]
    )

class DisplayUserService(DisplayBase):

    id: int
    user: DisplayUser
    service: DisplayService
    client: DisplayClient
    created_at: datetime

# ______________ USER <> OUTLET MAPPINGS ____________________
class UserOutletBase(BaseModel):
    user_id: int = Field(
        ..., 
        description="ID of the user.", 
        examples=[10]
    )
    outlet_id: int = Field(
        ..., 
        description="ID of the outlet assigned to the user.", 
        examples=[101]
    )

class UserOutletCreate(UserOutletBase):
    client_id: int = Field(
        ..., 
        description="The ID of the client this mapping belongs to.", 
        examples=[1]
    )

class DisplayUserOutlet(DisplayBase):
    id: int
    user: DisplayUser
    outlet: DisplayOutlet
    client: DisplayClient
    created_at: datetime
