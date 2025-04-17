from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..schemas import schemas
from ..database import models

router = APIRouter() 

#______________________________________ Outlet <> Service routes ______________________________________
@router.post("/outlet-service-mappings/", response_model=schemas.DisplayOutletService)
async def create_outlet_service_mapping(
    mapping: schemas.OutletServiceCreate, 
    db: Session = Depends(get_db)
):
    print(mapping)
    # Check if user service exists
    existing_mapping = db.query(models.OutletService).filter(
        (models.OutletService.outlet_id == mapping.outlet_id) &
        (models.OutletService.service_id == mapping.service_id)
    ).first()
    print(existing_mapping)
    if existing_mapping:
        print('exisiting mapping')
        raise HTTPException(
            status_code=400,
            detail="This Outlet <> Service mapping is already registered"
        )
    
    db_mapping = models.OutletService(
        outlet_id=mapping.outlet_id,
        service_id=mapping.service_id,
        client_id=mapping.client_id
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.get("/outlet-service-mappings/", response_model=List[schemas.DisplayOutletService])
async def read_outlet_service_mappings(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    outlet_service_mappings = db.query(models.OutletService).offset(skip).limit(limit).all()
    return outlet_service_mappings

@router.get("/outlet-service-mappings/client/{client_id}", response_model=List[schemas.DisplayOutletService])
async def read_outlet_service_mappings_of_clients(
    client_id: int, 
    db: Session = Depends(get_db)
):
    db_outlet_service_mappings = db.query(models.OutletService).filter(models.OutletService.client_id == client_id).all()
    if db_outlet_service_mappings is None:
        raise HTTPException(status_code=404, detail=f"Outlet <> Service mappings not found for client id : {client_id}")
    return db_outlet_service_mappings

@router.get("/outlet-service-mappings/{mapping_id}", response_model=schemas.DisplayOutletService)
async def read_role_service_mapping(
    mapping_id: int, 
    db: Session = Depends(get_db)
):
    db_outlet_service_mappings = db.query(models.OutletService).filter(models.OutletService.id == mapping_id).first()
    if db_outlet_service_mappings is None:
        raise HTTPException(status_code=404, detail=f"Outlet <> Service mappings not found for map id : {mapping_id}")
    return db_outlet_service_mappings


#______________________________________ User <> Service routes ______________________________________
@router.post("/user-service-mappings/", response_model=schemas.DisplayUserService)
async def create_user_service_mapping(
    mapping: schemas.UserServiceCreate, 
    db: Session = Depends(get_db)
):
    # Check if user service exists
    existing_mapping = db.query(models.UserService).filter(
        (models.UserService.user_id == mapping.user_id) &
        (models.UserService.service_id == mapping.service_id)
    ).first()
    if existing_mapping:
        raise HTTPException(
            status_code=400,
            detail="This User <> Service mapping is already registered"
        )
    
    db_mapping = models.UserService(
        user_id=mapping.user_id,
        service_id=mapping.service_id,
        client_id=mapping.client_id
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.get("/user-service-mappings/", response_model=List[schemas.DisplayUserService])
async def read_user_service_mappings(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    user_service_mappings = db.query(models.UserService).offset(skip).limit(limit).all()
    return user_service_mappings

@router.get("/user-service-mappings/client/{client_id}", response_model=List[schemas.DisplayUserService])
async def read_user_service_mappings_of_clients(
    client_id: int, 
    db: Session = Depends(get_db)
):
    db_user_service_mappings = db.query(models.UserService).filter(models.UserService.client_id == client_id).all()
    if db_user_service_mappings is None:
        raise HTTPException(status_code=404, detail=f"User <> Service mappings not found for client id : {client_id}")
    return db_user_service_mappings

@router.get("/user-service-mappings/{mapping_id}", response_model=schemas.DisplayUserService)
async def read_user_service_mapping(
    mapping_id: int, 
    db: Session = Depends(get_db)
):
    db_user_service_mapping = db.query(models.UserService).filter(models.UserService.id == mapping_id).first()
    if db_user_service_mapping is None:
        raise HTTPException(status_code=404, detail=f"User <> Service mappings not found for map id : {mapping_id}")
    return db_user_service_mapping

#______________________________________ User <> Outlet routes ______________________________________
@router.post("/user-outlet-mappings/", response_model=schemas.DisplayUserOutlet)
async def create_role_outlet_mapping(
    mapping: schemas.UserOutletCreate, 
    db: Session = Depends(get_db)
):
    # Check if user service exists
    existing_mapping = db.query(models.UserOutlet).filter(
        (models.UserOutlet.user_id == mapping.user_id) &
        (models.UserOutlet.outlet_id == mapping.outlet_id)
    ).first()
    if existing_mapping:
        raise HTTPException(
            status_code=400,
            detail="This User <> Outlet mapping is already registered"
        )
    
    db_mapping = models.UserOutlet(
        user_id=mapping.user_id,
        outlet_id=mapping.outlet_id,
        client_id=mapping.client_id
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.get("/user-outlet-mappings/", response_model=List[schemas.DisplayUserOutlet])
async def read_user_outlet_mappings(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):

    db_user_outlet_mappings = db.query(models.UserOutlet).offset(skip).limit(limit).all()
    return db_user_outlet_mappings

@router.get("/user-outlet-mappings/client/{client_id}", response_model=List[schemas.DisplayUserOutlet])
async def read_user_outlet_mappings_of_clients(
    client_id: int, 
    db: Session = Depends(get_db)
):
    db_user_outlet_mappings = db.query(models.UserOutlet).filter(models.UserOutlet.client_id == client_id).all()
    if db_user_outlet_mappings is None:
        raise HTTPException(status_code=404, detail=f"User <> Outlet mappings not found for client id : {client_id}")
    return db_user_outlet_mappings

@router.get("/user-outlet-mappings/{mapping_id}", response_model=schemas.DisplayUserOutlet)
async def read_role_outlet_mapping(
    mapping_id: int, 
    db: Session = Depends(get_db)
):
    db_role_outlet_mapping = db.query(models.UserOutlet).filter(models.UserOutlet.id == mapping_id).first()
    if db_role_outlet_mapping is None:
        raise HTTPException(status_code=404, detail=f"User <> Outlet mappings not found for map id : {mapping_id}")
    return db_role_outlet_mapping