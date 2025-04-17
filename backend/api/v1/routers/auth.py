from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from ..database.database import get_db
from ..schemas import schemas
from ..database import models

ACCESS_TOKEN_EXPIRE_MINUTES = 30
IST = timezone(timedelta(hours=5, minutes=30))

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire =  datetime.now(IST) + expires_delta
    else:
        expire = datetime.now(IST) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Get Email from session
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Check email in DB
    user = db.query(models.Client).filter(models.Client.email == email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: schemas.ClientInDB = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

router = APIRouter() 

#______________________________________ Client routes ______________________________________
# Registration endpoint (public)
@router.post("/clients/", response_model=schemas.DisplayClient)
async def register_client(
    client: schemas.ClientCreate, 
    db: Session = Depends(get_db)
):
    # Check if email already exists
    db_client = db.query(models.Client).filter(
        (models.Client.email == client.username)
    ).first()
    if db_client:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    print("client password ", client.password)
    print("decrypted pass ", client.password.get_secret_value())
    
    hashed_password = get_password_hash(client.password.get_secret_value())
    db_client = models.Client(
        username=client.username,
        email=client.email,
        hashed_password=hashed_password,
        accesstype=client.accesstype
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# Login endpoint (public)
@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    client = db.query(models.Client).filter(
        models.Client.email == form_data.username
    ).first()
    
    if not client or not verify_password(form_data.password, client.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": client.email}, expires_delta=access_token_expires
    )
    
    # # Update last login
    # client.last_login = datetime.now(IST)
    # db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

# Logout endpoint (would need token blacklist in production)
@router.post("/logout")
async def logout(
    current_user: schemas.ClientInDB = Depends(get_current_active_user)
):
    # Add the token to a blacklist
    return {"message": "Successfully logged out"}

# Protected route example
@router.get("/clients/me", response_model=schemas.DisplayClient)
async def read_client_me(
    current_user: schemas.ClientInDB = Depends(get_current_active_user)
):
    return current_user

# Protect all other routes by adding the dependency
@router.get("/protected-route")
async def protected_route(
    current_user: schemas.ClientInDB = Depends(get_current_active_user)
):
    return {"message": "This is a protected route", "user": current_user.username}

@router.get("/clients/", response_model=List[schemas.DisplayClient])
async def read_clients(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.ClientInDB = Depends(get_current_active_user)
):
    clients = db.query(models.Client).offset(skip).limit(limit).all()
    return clients

@router.get("/clients/{client_id}", response_model=schemas.DisplayClient)
async def read_client(
    client_id: int, 
    db: Session = Depends(get_db)
):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

