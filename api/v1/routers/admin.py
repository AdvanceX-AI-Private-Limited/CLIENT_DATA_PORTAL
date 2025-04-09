
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..schemas import schemas
from ..database import models


router = APIRouter() 

#______________________________________ Outlet routes ______________________________________
@router.post("/outlets/", response_model=schemas.DisplayOutlet)
async def create_outlet(
    outlet: schemas.OutletCreate, 
    db: Session = Depends(get_db)
):
    db_outlet = models.Outlet(
        aggregator=outlet.aggregator,
        resid=outlet.resid,
        subzone=outlet.subzone,
        city=outlet.city,
        outletnumber=outlet.outletnumber,
        is_active=outlet.is_active,
        client_id=outlet.clientid
    )
    db.add(db_outlet)
    db.commit()
    db.refresh(db_outlet)
    return db_outlet

@router.get("/outlets/", response_model=List[schemas.DisplayOutlet])
async def read_outlets(
    status: models.StatusEnum = models.StatusEnum.all,  # Add status filter (Active, Inactive, All)
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.Outlet)
    
    # Apply filter based on status
    if status == models.StatusEnum.active:
        query = query.filter(models.Outlet.is_active == True)
    elif status == models.StatusEnum.inactive:
        query = query.filter(models.Outlet.is_active == False)
    
    outlets = query.offset(skip).limit(limit).all()
    return outlets

@router.get("/outlets/client/{client_id}", response_model=List[schemas.DisplayOutlet])
async def read_outlet_of_clients(
    client_id: int, 
    db: Session = Depends(get_db)
):
    db_outlet = db.query(models.Outlet).filter(models.Outlet.client_id == client_id).all()
    if db_outlet is None:
        raise HTTPException(status_code=404, detail="Outlets not found for client_id")
    return db_outlet

@router.get("/outlets/{outlet_id}", response_model=schemas.DisplayOutlet)
async def read_outlet(
    outlet_id: int, 
    db: Session = Depends(get_db)
):
    db_outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id).first()
    if db_outlet is None:
        raise HTTPException(status_code=404, detail="Outlet not found")
    return db_outlet


#______________________________________ User routes ______________________________________
@router.post("/users/", response_model=schemas.DisplayUser)
async def create_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    db_user = models.User(
        username=user.username,
        usernumber=user.usernumber,
        useremail=user.useremail,
        client_id=user.clientid
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/", response_model=List[schemas.DisplayUser])
async def read_users(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/users/client/{client_id}", response_model=List[schemas.DisplayUser])
async def read_users_of_clients(
    client_id: int, 
    db: Session = Depends(get_db)
):
    db_users = db.query(models.User).filter(models.User.client_id == client_id).all()
    if db_users is None:
        raise HTTPException(status_code=404, detail="Users not found for client_id")
    return db_users

@router.get("/users/{user_id}", response_model=schemas.DisplayUser)
async def read_user(
    user_id: int, 
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


#______________________________________ Role routes ______________________________________
@router.post("/roles/", response_model=schemas.DisplayRole)
async def create_role(
    role: schemas.RoleCreate, 
    db: Session = Depends(get_db)
):
    db_role = models.Role(
        rolename=role.rolename,
        client_id=role.clientid
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@router.get("/roles/", response_model=List[schemas.DisplayRole])
async def read_roles(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    roles = db.query(models.Role).offset(skip).limit(limit).all()
    return roles

@router.get("/roles/client/{client_id}", response_model=List[schemas.DisplayRole])
async def read_users_of_clients(
    client_id: int, 
    db: Session = Depends(get_db)
):
    db_roles = db.query(models.Role).filter(models.Role.client_id == client_id).all()
    if db_roles is None:
        raise HTTPException(status_code=404, detail="Roles not found for client_id")
    return db_roles

@router.get("/roles/{role_id}", response_model=schemas.DisplayRole)
async def read_role(
    role_id: int, 
    db: Session = Depends(get_db)
):
    db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


#______________________________________ Service routes ______________________________________
@router.post("/services/", response_model=schemas.DisplayService)
async def create_service(
    service: schemas.ServiceCreate, 
    db: Session = Depends(get_db)
):
    db_service = models.Service(
        servicename=service.servicename,
        servicevariant=service.servicevariant
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.get("/services/", response_model=List[schemas.DisplayService])
async def read_services(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    roles = db.query(models.Service).offset(skip).limit(limit).all()
    return roles

@router.get("/services/{service_id}", response_model=schemas.DisplayService)
async def read_service(
    service_id: int, 
    db: Session = Depends(get_db)
):
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service

