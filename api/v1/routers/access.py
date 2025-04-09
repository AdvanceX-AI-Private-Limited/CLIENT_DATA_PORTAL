from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..import schemas
from ..import models

router = APIRouter() 

#______________________________________ Role <> Service routes ______________________________________
@router.post("/role-service-mappings/", response_model=schemas.DisplayRoleServiceMapping)
async def create_role_service_mapping(
    mapping: schemas.RoleServiceMappingCreate, 
    db: Session = Depends(get_db)
):
    db_mapping = models.RoleServiceMapping(
        role_id=mapping.roleid,
        service_id=mapping.serviceid,
        client_id=mapping.clientid
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.get("/role-service-mappings/", response_model=List[schemas.DisplayRoleServiceMapping])
async def read_role_service_mappings(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    role_service_mappings = db.query(models.RoleServiceMapping).offset(skip).limit(limit).all()
    return role_service_mappings

@router.get("/role-service-mappings/client/{client_id}", response_model=List[schemas.DisplayRoleServiceMapping])
async def read_role_service_mappings_of_clients(
    client_id: int, 
    db: Session = Depends(get_db)
):
    db_role_service_mappings = db.query(models.RoleServiceMapping).filter(models.RoleServiceMapping.client_id == client_id).all()
    if db_role_service_mappings is None:
        raise HTTPException(status_code=404, detail="Role <> Service mappings not found for client_id")
    return db_role_service_mappings

@router.get("/role-service-mappings/{mapping_id}", response_model=schemas.DisplayRoleServiceMapping)
async def read_role_service_mapping(
    mapping_id: int, 
    db: Session = Depends(get_db)
):
    db_role_service_mappings = db.query(models.RoleServiceMapping).filter(models.RoleServiceMapping.id == mapping_id).first()
    if db_role_service_mappings is None:
        raise HTTPException(status_code=404, detail="Role <> Service mappings not found")
    return db_role_service_mappings


#______________________________________ Role <> User routes ______________________________________
@router.post("/role-user-mappings/", response_model=schemas.DisplayRoleUserMapping)
async def create_role_user_mapping(
    mapping: schemas.RoleUserMappingCreate, 
    db: Session = Depends(get_db)
):
    db_mapping = models.RoleUserMapping(
        role_id=mapping.roleid,
        user_id=mapping.userid,
        client_id=mapping.clientid
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.get("/role-user-mappings/", response_model=List[schemas.DisplayRoleUserMapping])
async def read_role_user_mappings(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    role_user_mappings = db.query(models.RoleUserMapping).offset(skip).limit(limit).all()
    return role_user_mappings

@router.get("/role-user-mappings/client/{client_id}", response_model=List[schemas.DisplayRoleUserMapping])
async def read_role_user_mappings_of_clients(
    client_id: int, 
    db: Session = Depends(get_db)
):
    db_role_user_mappings = db.query(models.RoleUserMapping).filter(models.RoleUserMapping.client_id == client_id).all()
    if db_role_user_mappings is None:
        raise HTTPException(status_code=404, detail="Role <> User mappings not found for client_id")
    return db_role_user_mappings

@router.get("/role-user-mappings/{mapping_id}", response_model=schemas.DisplayRoleUserMapping)
async def read_role_user_mapping(
    mapping_id: int, 
    db: Session = Depends(get_db)
):
    db_role_user_mapping = db.query(models.RoleUserMapping).filter(models.RoleUserMapping.id == mapping_id).first()
    if db_role_user_mapping is None:
        raise HTTPException(status_code=404, detail="Role <> User mappings not found")
    return db_role_user_mapping

#______________________________________ Role <> Outlet routes ______________________________________
@router.post("/role-outlet-mappings/", response_model=schemas.DisplayRoleOutletMapping)
async def create_role_outlet_mapping(
    mapping: schemas.RoleOutletMappingCreate, 
    db: Session = Depends(get_db)
):
    db_mapping = models.RoleOutletMapping(
        role_id=mapping.roleid,
        outlet_id=mapping.outletid,
        client_id=mapping.clientid
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.get("/role-outlet-mappings/", response_model=List[schemas.DisplayRoleOutletMapping])
async def read_role_outlet_mappings(
    status: models.StatusEnum = models.StatusEnum.all, # Only Accepts - Active, Inactive and All 
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):

    query = db.query(models.RoleOutletMapping) # Doesnt fetch data, only builds query (lazy evaluation)

    if status != models.StatusEnum.all:
        query = query.join(models.RoleOutletMapping.outlet)

        if status == models.StatusEnum.active:
            query = query.filter(models.Outlet.is_active == True)
        elif status == models.StatusEnum.inactive:
            query = query.filter(models.Outlet.is_active == False)
        # No filter applied if status is 'All'
        
    db_role_outlet_mappings = query.offset(skip).limit(limit).all() # Runs here when .all() action is ran
    return db_role_outlet_mappings

@router.get("/role-outlet-mappings/client/{client_id}", response_model=List[schemas.DisplayRoleOutletMapping])
async def read_role_outlet_mappings_of_clients(
    client_id: int, 
    db: Session = Depends(get_db)
):
    db_role_outlet_mappings = db.query(models.RoleOutletMapping).filter(models.RoleOutletMapping.client_id == client_id).all()
    if db_role_outlet_mappings is None:
        raise HTTPException(status_code=404, detail="Role <> Outlet mappings not found for client_id")
    return db_role_outlet_mappings

@router.get("/role-outlet-mappings/{mapping_id}", response_model=schemas.DisplayRoleOutletMapping)
async def read_role_outlet_mapping(
    mapping_id: int, 
    db: Session = Depends(get_db)
):
    db_role_outlet_mapping = db.query(models.RoleOutletMapping).filter(models.RoleOutletMapping.id == mapping_id).first()
    if db_role_outlet_mapping is None:
        raise HTTPException(status_code=404, detail="Role <> Outlet mappings not found")
    return db_role_outlet_mapping