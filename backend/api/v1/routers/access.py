from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .admin import verify_request
from .auth import get_current_session
from ..database.database import get_db
from ..schemas import schemas
from ..database import models
from logger import create_logger

# Initialize logger
logger = create_logger(__name__)

router = APIRouter() 
INTERNAL_CLIENT_IDS = {1}

#______________________________________ Outlet <> Service routes ______________________________________
@router.post("/outlet-service-mappings/", response_model=List[schemas.DisplayOutletService])
async def create_outlet_service_mapping(
    mappings: List[schemas.OutletServiceCreate], 
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to map {len(mappings)} mappings by client ID: {current_session.client_id}")

    created_mappings = []

    for mapping in mappings:
        logger.info(f"Processing Map: outlet={mapping.outlet_id}, service={mapping.service_id}")

        # Check if outlet exists
        existing_outlet = db.query(models.Outlet).filter(
            (models.Outlet.id == mapping.outlet_id)
        ).first()
        if not existing_outlet:
            logger.warning(f"Unknown outlet ID: {mapping.outlet_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown outlet ID passed"
            )
        
        # Check if service exists
        existing_service = db.query(models.Service).filter(
            (models.Service.id == mapping.service_id)
        ).first()
        if not existing_service:
            logger.warning(f"Unknown service ID: {mapping.service_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown service ID passed"
            )

        # Check if mapping exists
        existing_mapping = db.query(models.OutletService).filter(
            (models.OutletService.outlet_id == mapping.outlet_id) &
            (models.OutletService.service_id == mapping.service_id)
        ).first()
        if existing_mapping:
            logger.warning("This Outlet <> Service mapping is already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This Outlet <> Service mapping is already registered"
            )
        
        db_mapping = models.OutletService(
            outlet_id=mapping.outlet_id,
            service_id=mapping.service_id,
            client_id=mapping.client_id
        )
        db.add(db_mapping)
        try:
            db.commit()
            db.refresh(db_mapping)
            logger.info(f"Successfully created mapping: outlet={mapping.outlet_id} to service={mapping.service_id}")
            created_mappings.append(db_mapping)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create mapping: outlet={mapping.outlet_id} to service={mapping.service_id}, error={str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Failed to create outlet due to internal error"
                )

    if not created_mappings:
        logger.warning("No new mappings were created. All were duplicates or failed.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No mappings were created. All were duplicates or failed."
            )

    logger.info(f"Successfully created {len(created_mappings)} mappings")
    return created_mappings

@router.get("/outlet-service-mappings/", response_model=List[schemas.DisplayOutletService])
async def read_outlet_service_mappings(
    params: schemas.QueryOutletService, 
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to get mappings with params : {params}")

    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    logger.info(f"Client ID {current_session.client_id} is_internal_client={is_internal_client}")

    # Only verify request for non-internal clients
    if not is_internal_client:
        if params.outlet_id:
            try:
                verify_request(client_id=current_session.client_id, 
                            outlet_id=params.outlet_id,
                            db=db)
            except Exception as e:
                logger.error(f"Request verification failed: {str(e)}")
                raise HTTPException(
                    status_code=403,
                    detail="Unauthorized access to update outlet"
                )

    query = db.query(models.OutletService)

    try:
        query = db.query(models.OutletService)

        if not is_internal_client:

            if params.client_id is not None:
                logger.info(f"Filtering mappings by client ID {params.client_id}")
                query = query.filter(models.OutletService.client_id == params.client_id)

            if params.outlet_id is not None:
                logger.info(f"Filtering mappings by outlet ID {params.outlet_id}")
                query = query.filter(models.OutletService.outlet_id == params.outlet_id)

            if params.service_id is not None:
                logger.info(f"Filtering mappings by service ID {params.service_id}")
                query = query.filter(models.OutletService.service_id == params.service_id)

        allmappings = query.offset(params.skip).limit(params.limit).all()
        logger.info(f"Retrieved {len(allmappings)} mappings with skip={params.skip}, limit={params.limit}")

        return allmappings

    except Exception as e:
        logger.error(f"Error while retrieving mappings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mappings")


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