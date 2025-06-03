from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import datetime
from .auth import get_password_hash, verify_password
from ..database.database import get_db
from ..schemas import schemas
from ..database import models

router = APIRouter() 

#______________________________________ Client routes ______________________________________
# READ - Get all clients with pagination and filtering
@router.get("/", response_model=List[schemas.DisplayClient])
async def get_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    accesstype: Optional[str] = Query(None, description="Filter by access type"),
    search: Optional[str] = Query(None, description="Search by username or email"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Client)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(models.Client.is_active == is_active)
    
    if accesstype:
        query = query.filter(models.Client.accesstype == accesstype)
    
    if search:
        query = query.filter(
            or_(
                models.Client.username.ilike(f"%{search}%"),
                models.Client.email.ilike(f"%{search}%")
            )
        )
    
    clients = query.offset(skip).limit(limit).all()
    return clients

# READ - Get client by ID
@router.get("/{client_id}", response_model=schemas.DisplayClient)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    return client

# READ - Get client by username
@router.get("/username/{username}", response_model=schemas.DisplayClient)
async def get_client_by_username(
    username: str,
    db: Session = Depends(get_db)
):
    client = db.query(models.Client).filter(models.Client.username == username).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with username '{username}' not found"
        )
    return client

# READ - Get client by email
@router.get("/email/{email}", response_model=schemas.DisplayClient)
async def get_client_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    client = db.query(models.Client).filter(models.Client.email == email).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with email '{email}' not found"
        )
    return client

# # UPDATE - Update client (partial update)
# @router.patch("/{client_id}", response_model=schemas.DisplayClient)
# async def update_client(
#     client_id: int,
#     client_update: schemas.ClientUpdate,
#     db: Session = Depends(get_db)
# ):
#     # Get the existing client
#     db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
#     if not db_client:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Client with id {client_id} not found"
#         )
    
#     # Check for duplicate username (if being updated)
#     if client_update.username and client_update.username != db_client.username:
#         existing_username = db.query(models.Client).filter(
#             models.Client.username == client_update.username,
#             models.Client.id != client_id
#         ).first()
#         if existing_username:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Username already taken"
#             )
    
#     # Check for duplicate email (if being updated)
#     if client_update.email and client_update.email != db_client.email:
#         existing_email = db.query(models.Client).filter(
#             models.Client.email == client_update.email,
#             models.Client.id != client_id
#         ).first()
#         if existing_email:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Email already registered"
#             )
    
#     # Update fields that are provided
#     update_data = client_update.model_dump(exclude_unset=True)
    
#     # Handle password update separately
#     if "password" in update_data:
#         password_value = update_data.pop("password")
#         if password_value:
#             db_client.hashed_password = get_password_hash(password_value.get_secret_value())
    
#     # Update other fields
#     for field, value in update_data.items():
#         setattr(db_client, field, value)
    
#     # Update the timestamp
#     db_client.updated_at = datetime.now()
    
#     db.commit()
#     db.refresh(db_client)
#     return db_client

# # UPDATE - Replace entire client (full update)
# @router.put("/{client_id}", response_model=schemas.DisplayClient)
# async def replace_client(
#     client_id: int,
#     client_data: schemas.ClientReplace,
#     db: Session = Depends(get_db)
# ):
#     # Get the existing client
#     db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
#     if not db_client:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Client with id {client_id} not found"
#         )
    
#     # Check for duplicate username
#     if client_data.username != db_client.username:
#         existing_username = db.query(models.Client).filter(
#             models.Client.username == client_data.username,
#             models.Client.id != client_id
#         ).first()
#         if existing_username:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Username already taken"
#             )
    
#     # Check for duplicate email
#     if client_data.email != db_client.email:
#         existing_email = db.query(models.Client).filter(
#             models.Client.email == client_data.email,
#             models.Client.id != client_id
#         ).first()
#         if existing_email:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Email already registered"
#             )
    
#     # Update all fields
#     db_client.username = client_data.username
#     db_client.email = client_data.email
#     db_client.accesstype = client_data.accesstype
#     db_client.is_active = client_data.is_active
    
#     # Handle password if provided
#     if client_data.password:
#         db_client.hashed_password = get_password_hash(client_data.password.get_secret_value())
    
#     # Update timestamp
#     db_client.updated_at = datetime.now()
    
#     db.commit()
#     db.refresh(db_client)
#     return db_client

# UPDATE - Activate/Deactivate client
@router.patch("/{client_id}/status", response_model=schemas.DisplayClient)
async def toggle_client_status(
    client_id: int,
    is_active: bool,
    db: Session = Depends(get_db)
):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    db_client.is_active = is_active
    db_client.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_client)
    return db_client

# # UPDATE - Change password
# @router.patch("/{client_id}/password", response_model=dict)
# async def change_client_password(
#     client_id: int,
#     password_data: schemas.PasswordChange,
#     db: Session = Depends(get_db)
# ):
#     db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
#     if not db_client:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Client with id {client_id} not found"
#         )
    
#     # Verify current password
#     if not verify_password(password_data.current_password.get_secret_value(), db_client.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Current password is incorrect"
#         )
    
#     # Update to new password
#     db_client.hashed_password = get_password_hash(password_data.new_password.get_secret_value())
#     db_client.updated_at = datetime.now()
    
#     db.commit()
#     return {"message": "Password updated successfully"}

# DELETE - Soft delete (deactivate) client
@router.delete("/{client_id}/soft", response_model=dict)
async def soft_delete_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    db_client.is_active = False
    db_client.updated_at = datetime.now()
    
    db.commit()
    return {"message": f"Client {client_id} has been deactivated"}

# DELETE - Hard delete client (permanent deletion)
@router.delete("/{client_id}", response_model=dict)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    # Note: This will cascade delete all related records due to your model relationships
    db.delete(db_client)
    db.commit()
    return {"message": f"Client {client_id} has been permanently deleted"}

# UTILITY - Get client statistics
@router.get("/stats/overview", response_model=dict)
async def get_client_stats(
    db: Session = Depends(get_db)
):
    total_clients = db.query(models.Client).count()
    active_clients = db.query(models.Client).filter(models.Client.is_active == True).count()
    inactive_clients = total_clients - active_clients
    
    # Get clients by access type
    access_types = db.query(models.Client.accesstype, db.func.count(models.Client.id))\
        .group_by(models.Client.accesstype).all()
    
    return {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "inactive_clients": inactive_clients,
        "clients_by_access_type": dict(access_types)
    }
