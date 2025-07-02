from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
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

@router.get("/outlet-service-mappings/")
async def read_outlet_service_mappings(
    params: schemas.QueryOutletService = Depends(), 
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
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized access to get outlet"
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

        # If grouped, return custom schema (list of dicts)
        if allmappings and getattr(params, "grouped", False):
            result = []
            for m in allmappings:
                result.append({
                    "mapping_id": m.id,
                    "aggregator": getattr(m.outlet, "aggregator", None),
                    "resid": getattr(m.outlet, "resid", None),
                    "subzone": getattr(m.outlet, "subzone", None),
                    "resshortcode": getattr(m.outlet, "resshortcode", None),
                    "city": getattr(m.outlet, "city", None),
                    "is_active": getattr(m.outlet, "is_active", None),
                    "servicename": getattr(m.service, "servicename", None),
                    "servicevariant": getattr(m.service, "servicevariant", None)
                })
            return result
        # Default: return as per DisplayOutletService schema
        return [schemas.DisplayOutletService.model_validate(m) for m in allmappings]

    except Exception as e:
        logger.error(f"Error while retrieving mappings: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve mappings")

@router.put("/outlet-service-mappings/{mapping_id}", response_model=schemas.DisplayOutletService)
async def update_outlet_service_mapping(
    mapping_id: int,
    mapping_update: schemas.UpdateOutletServiceMapping,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to update OutletService Mapping with ID {mapping_id}")

    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    logger.info(f"Client ID {current_session.client_id} is_internal_client={is_internal_client}")

    if not is_internal_client:
        is_client_same = (
            hasattr(current_session, "client_id") and 
            hasattr(mapping_update, "client_id") and 
            current_session.client_id == mapping_update.client_id
        )
        logger.info(f"Client ID match check: {is_client_same}")

        if is_client_same:
            try:
                verify_request(
                    client_id=current_session.client_id, 
                    outlet_service_mapping_id=mapping_id,
                    db=db
                )
                logger.info(f"Request verification successful for client {current_session.client_id}")
            except Exception as e:
                logger.error(f"Request verification failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized access to update OutletService Mapping"
                )

    logger.info(f"Fetching OutletService Mapping with ID {mapping_id}")
    db_mapping = db.query(models.OutletService).filter(models.OutletService.id == mapping_id).first()

    if not db_mapping:
        logger.warning(f"OutletService Mapping with ID {mapping_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OutletService Mapping with ID {mapping_id} not found"
        )

    logger.info(f"Checking for duplicates: outlet_id={mapping_update.outlet_id} <> service_id={mapping_update.service_id}")
    existing = db.query(models.User).filter(
        models.OutletService.outlet_id == mapping_update.outlet_id,
        models.OutletService.service_id == mapping_update.service_id,
        models.OutletService.id != mapping_id  # exclude current record
    ).first()
    if existing:
        logger.warning("Duplicate OutletService Mapping found with same outlet and service")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Another OutletService Mapping with the same outlet and service already exists."
        )

    updated_fields = mapping_update.model_dump(exclude_unset=True)
    logger.info(f"Updating fields: {updated_fields}")
    for field, value in updated_fields.items():
        setattr(db_mapping, field, value)

    try:
        db.commit()
        db.refresh(db_mapping)
        logger.info(f"Successfully updated OutletService Mapping with ID {mapping_id}")
    except Exception as e:
        logger.error(f"Failed to update OutletService Mapping ID {mapping_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating OutletService Mapping"
        )

    return db_mapping

@router.delete("/outlet-service-mappings/{mapping_id}", status_code=200)
async def delete_outlet_service_mapping(
    mapping_id: int,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
    ):
    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    # Only verify request for non-internal clients
    if not is_internal_client:
        try:
            verify_request(
                client_id=current_session.client_id, 
                outlet_service_mapping_id=mapping_id,
                db=db
            )
            logger.info(f"Request verification successful for client {current_session.client_id}")
        except Exception as e:
            logger.error(f"Request verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to update OutletService Mapping"
            )
            
    try:
        logger.info(f"Attempting to delete OutletService Mapping with ID {mapping_id}")
        db_mapping = db.query(models.OutletService).filter(models.OutletService.id == mapping_id).first()

        if not db_mapping:
            logger.warning(f"OutletService Mapping with ID {mapping_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OutletService Mapping with ID {mapping_id} not found"
            )

        db.delete(db_mapping)
        db.commit()
        logger.info(f"Successfully deleted OutletService Mapping with ID {mapping_id}")
        return JSONResponse(
            content={"message": f"OutletService Mapping with ID {mapping_id} successfully deleted"},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error occurred while deleting OutletService Mapping ID {mapping_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the OutletService Mapping"
        )


#______________________________________ User <> Service routes ______________________________________
@router.post("/user-service-mappings/", response_model=List[schemas.DisplayUserService])
async def create_user_service_mapping(
    mappings: List[schemas.UserServiceCreate], 
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to map {len(mappings)} mappings by client ID: {current_session.client_id}")

    created_mappings = []

    for mapping in mappings:
        logger.info(f"Processing Map: user={mapping.user_id}, service={mapping.service_id}")

        # Check if user exists
        existing_user = db.query(models.User).filter(
            (models.User.id == mapping.user_id)
        ).first()
        if not existing_user:
            logger.warning(f"Unknown user ID: {mapping.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown user ID passed"
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
        existing_mapping = db.query(models.UserService).filter(
            (models.UserService.user_id == mapping.user_id) &
            (models.UserService.service_id == mapping.service_id)
        ).first()
        if existing_mapping:
            logger.warning("This User <> Service mapping is already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This User <> Service mapping is already registered"
            )
        
        db_mapping = models.UserService(
            user_id=mapping.user_id,
            service_id=mapping.service_id,
            client_id=mapping.client_id
        )
        db.add(db_mapping)
        try:
            db.commit()
            db.refresh(db_mapping)
            logger.info(f"Successfully created mapping: user={mapping.user_id} to service={mapping.service_id}")
            created_mappings.append(db_mapping)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create mapping: user={mapping.user_id} to service={mapping.service_id}, error={str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Failed to create user due to internal error"
                )

    if not created_mappings:
        logger.warning("No new mappings were created. All were duplicates or failed.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No mappings were created. All were duplicates or failed."
            )

    logger.info(f"Successfully created {len(created_mappings)} mappings")
    return created_mappings


@router.get("/user-service-mappings/")
async def read_user_service_mappings(
    params: schemas.QueryUserService = Depends(), 
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to get mappings with params : {params}")

    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    logger.info(f"Client ID {current_session.client_id} is_internal_client={is_internal_client}")

    # Only verify request for non-internal clients
    if not is_internal_client:
        if params.user_id:
            try:
                verify_request(client_id=current_session.client_id, 
                            user_id=params.user_id,
                            db=db)
            except Exception as e:
                logger.error(f"Request verification failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized access to get user"
                )

    query = db.query(models.UserService)

    try:
        query = db.query(models.UserService)

        if not is_internal_client:
            if params.client_id is not None:
                logger.info(f"Filtering mappings by client ID {params.client_id}")
                query = query.filter(models.UserService.client_id == params.client_id)
            if params.user_id is not None:
                logger.info(f"Filtering mappings by user ID {params.user_id}")
                query = query.filter(models.UserService.user_id == params.user_id)
            if params.service_id is not None:
                logger.info(f"Filtering mappings by service ID {params.service_id}")
                query = query.filter(models.UserService.service_id == params.service_id)

        allmappings = query.offset(params.skip).limit(params.limit).all()
        logger.info(f"Retrieved {len(allmappings)} mappings with skip={params.skip}, limit={params.limit}")

        if allmappings and getattr(params, "grouped", False):
            result = []
            logger.info("Grouping mappings by user and service: ", allmappings)
            for m in allmappings:
                mapping_id = m.id
                user = m.user
                service = m.service
                service_id = m.service_id
                created_at = m.created_at
                user_id = m.user_id
                client_id = m.client_id
                
                if not user or not service:
                    continue
                result.append({
                    "mapping_id": mapping_id,
                    "username": getattr(user, "username", None),
                    "usernumber": str(getattr(user, "usernumber", "")),
                    "useremail": getattr(user, "useremail", None),
                    "service": getattr(service, "servicename", getattr(service, "id", None)),
                    "service_variant": getattr(service, "servicevariant", None),
                    "service_id": service_id,
                    "created_at": created_at,
                    "user_id": user_id,
                    "client_id": client_id
                })
            return result
        else:
            return allmappings

    except Exception as e:
        logger.error(f"Error while retrieving mappings: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve mappings")

@router.put("/user-service-mappings/{mapping_id}", response_model=schemas.DisplayUserService)
async def update_user_service_mapping(
    mapping_id: int,
    mapping_update: schemas.UpdateUserServiceMapping,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to update UserService Mapping with ID {mapping_id}")

    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    logger.info(f"Client ID {current_session.client_id} is_internal_client={is_internal_client}")

    if not is_internal_client:
        is_client_same = (
            hasattr(current_session, "client_id") and 
            hasattr(mapping_update, "client_id") and 
            current_session.client_id == mapping_update.client_id
        )
        logger.info(f"Client ID match check: {is_client_same}")

        if is_client_same:
            try:
                verify_request(
                    client_id=current_session.client_id, 
                    user_service_mapping_id=mapping_id,
                    db=db
                )
                logger.info(f"Request verification successful for client {current_session.client_id}")
            except Exception as e:
                logger.error(f"Request verification failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized access to update UserService Mapping"
                )

    logger.info(f"Fetching UserService Mapping with ID {mapping_id}")
    db_mapping = db.query(models.UserService).filter(models.UserService.id == mapping_id).first()

    if not db_mapping:
        logger.warning(f"UserService Mapping with ID {mapping_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UserService Mapping with ID {mapping_id} not found"
        )

    logger.info(f"Checking for duplicates: user_id={mapping_update.user_id} <> service_id={mapping_update.service_id}")
    existing = db.query(models.User).filter(
        models.UserService.user_id == mapping_update.user_id,
        models.UserService.service_id == mapping_update.service_id,
        models.UserService.id != mapping_id  # exclude current record
    ).first()
    if existing:
        logger.warning("Duplicate UserService Mapping found with same user and service")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Another UserService Mapping with the same user and service already exists."
        )

    updated_fields = mapping_update.model_dump(exclude_unset=True)
    logger.info(f"Updating fields: {updated_fields}")
    for field, value in updated_fields.items():
        setattr(db_mapping, field, value)

    try:
        db.commit()
        db.refresh(db_mapping)
        logger.info(f"Successfully updated UserService Mapping with ID {mapping_id}")
    except Exception as e:
        logger.error(f"Failed to update UserService Mapping ID {mapping_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating UserService Mapping"
        )

    return db_mapping

@router.delete("/user-service-mappings/{mapping_id}", status_code=200)
async def delete_user_service_mapping(
    mapping_id: int,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
    ):
    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    # Only verify request for non-internal clients
    if not is_internal_client:
        try:
            verify_request(
                client_id=current_session.client_id, 
                user_service_mapping_id=mapping_id,
                db=db
            )
            logger.info(f"Request verification successful for client {current_session.client_id}")
        except Exception as e:
            logger.error(f"Request verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to update UserService Mapping"
            )
            
    try:
        logger.info(f"Attempting to delete UserService Mapping with ID {mapping_id}")
        db_mapping = db.query(models.UserService).filter(models.UserService.id == mapping_id).first()

        if not db_mapping:
            logger.warning(f"UserService Mapping with ID {mapping_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"UserService Mapping with ID {mapping_id} not found"
            )

        db.delete(db_mapping)
        db.commit()
        logger.info(f"Successfully deleted UserService Mapping with ID {mapping_id}")
        return JSONResponse(
            content={"message": f"UserService Mapping with ID {mapping_id} successfully deleted"},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error occurred while deleting UserService Mapping ID {mapping_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the UserService Mapping"
        )


#______________________________________ User <> Outlet routes ______________________________________
@router.post("/user-outlet-mappings/", response_model=List[schemas.DisplayUserOutlet])
async def create_user_outlet_mapping(
    mappings: List[schemas.UserOutletCreate], 
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to map {len(mappings)} mappings by client ID: {current_session.client_id}")

    created_mappings = []

    for mapping in mappings:
        logger.info(f"Processing Map: user={mapping.user_id}, outlet={mapping.outlet_id}")

        # Check if user exists
        existing_user = db.query(models.User).filter(
            (models.User.id == mapping.user_id)
        ).first()
        if not existing_user:
            logger.warning(f"Unknown user ID: {mapping.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown user ID passed"
            )
        
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

        # Check if mapping exists
        existing_mapping = db.query(models.UserOutlet).filter(
            (models.UserOutlet.user_id == mapping.user_id) &
            (models.UserOutlet.outlet_id == mapping.outlet_id)
        ).first()
        if existing_mapping:
            logger.warning("This User <> Outlet mapping is already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This User <> Outlet mapping is already registered"
            )
        
        db_mapping = models.UserOutlet(
            user_id=mapping.user_id,
            outlet_id=mapping.outlet_id,
            client_id=mapping.client_id
        )
        db.add(db_mapping)
        try:
            db.commit()
            db.refresh(db_mapping)
            logger.info(f"Successfully created mapping: user={mapping.user_id} to outlet={mapping.outlet_id}")
            created_mappings.append(db_mapping)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create mapping: user={mapping.user_id} to outlet={mapping.outlet_id}, error={str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Failed to create user due to internal error"
                )

    if not created_mappings:
        logger.warning("No new mappings were created. All were duplicates or failed.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No mappings were created. All were duplicates or failed."
            )

    logger.info(f"Successfully created {len(created_mappings)} mappings")
    return created_mappings

@router.get("/user-outlet-mappings/")
async def read_user_outlet_mappings(
    params: schemas.QueryUserOutlet = Depends(),
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to get mappings with params : {params}")

    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    # is_internal_client = True
    logger.info(f"Client ID {current_session.client_id} is_internal_client={is_internal_client}")

    # Only verify request for non-internal clients
    if not is_internal_client:
        if params.user_id:
            try:
                verify_request(client_id=current_session.client_id, 
                            user_id=params.user_id,
                            db=db)
            except Exception as e:
                logger.error(f"Request verification failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized access to get user"
                )

    query = db.query(models.UserOutlet)

    try:
        query = db.query(models.UserOutlet)

        if not is_internal_client:

            if params.client_id is not None:
                logger.info(f"Filtering mappings by client ID {params.client_id}")
                query = query.filter(models.UserOutlet.client_id == params.client_id)

            if params.user_id is not None:
                logger.info(f"Filtering mappings by user ID {params.user_id}")
                query = query.filter(models.UserOutlet.user_id == params.user_id)

            if params.outlet_id is not None:
                logger.info(f"Filtering mappings by outlet ID {params.outlet_id}")
                query = query.filter(models.UserOutlet.outlet_id == params.outlet_id)

        allmappings = query.offset(params.skip).limit(params.limit).all()
        logger.info(f"Retrieved {len(allmappings)} mappings with skip={params.skip}, limit={params.limit}")

        if allmappings:
            if params.grouped:
                grouped = {}
                for m in allmappings:
                    outlet = m.outlet
                    user = m.user
                    res_id = outlet.id
                    mapping_id = m.id
                    brandname = outlet.brand.brandname if outlet and outlet.brand else None
                    key = res_id
                    if key not in grouped:
                        grouped[key] = {
                            "aggregator": outlet.aggregator,
                            "brand": brandname,
                            "res_id": res_id,
                            "shortcode": outlet.resshortcode,
                            "users": set()
                        }
                    grouped[key]["users"].add(user.username)

                response = []
                for g in grouped.values():
                    response.append(
                        schemas.DisplayUserOutletGrouped(
                            aggregator=g["aggregator"],
                            brand=g["brand"],
                            res_id=g["res_id"],
                            shortcode=g["shortcode"],
                            users=list(g["users"]),
                        )
                    )
                return response
            else:
                result = []
                for m in allmappings:
                    user = m.user
                    result.append({
                        "email": getattr(user, "useremail", ""),
                        "name": getattr(user, "username", ""),
                        "number": str(getattr(user, "usernumber", "")),
                        "mapping_id": m.id
                    })
                return result
                # return [
                #     schemas.DisplayUserOutlet.from_orm(m) for m in allmappings
                # ]
            
    except Exception as e:
        logger.error(f"Error while retrieving mappings: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve mappings")
    

@router.put("/user-outlet-mappings/{mapping_id}", response_model=schemas.DisplayUserOutlet)
async def update_user_outlet_mapping(
    mapping_id: int,
    mapping_update: schemas.UpdateUserOutletMapping,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to update UserOutlet Mapping with ID {mapping_id}")

    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    logger.info(f"Client ID {current_session.client_id} is_internal_client={is_internal_client}")

    if not is_internal_client:
        is_client_same = (
            hasattr(current_session, "client_id") and 
            hasattr(mapping_update, "client_id") and 
            current_session.client_id == mapping_update.client_id
        )
        logger.info(f"Client ID match check: {is_client_same}")

        if is_client_same:
            try:
                verify_request(
                    client_id=current_session.client_id, 
                    user_outlet_mapping_id=mapping_id,
                    db=db
                )
                logger.info(f"Request verification successful for client {current_session.client_id}")
            except Exception as e:
                logger.error(f"Request verification failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized access to update UserOutlet Mapping"
                )

    logger.info(f"Fetching UserOutlet Mapping with ID {mapping_id}")
    db_mapping = db.query(models.UserOutlet).filter(models.UserOutlet.id == mapping_id).first()

    if not db_mapping:
        logger.warning(f"UserOutlet Mapping with ID {mapping_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UserOutlet Mapping with ID {mapping_id} not found"
        )

    logger.info(f"Checking for duplicates: user_id={mapping_update.user_id} <> outlet_id={mapping_update.outlet_id}")
    existing = db.query(models.User).filter(
        models.UserOutlet.user_id == mapping_update.user_id,
        models.UserOutlet.outlet_id == mapping_update.outlet_id,
        models.UserOutlet.id != mapping_id  # exclude current record
    ).first()
    if existing:
        logger.warning("Duplicate UserOutlet Mapping found with same user and outlet")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Another UserOutlet Mapping with the same user and outlet already exists."
        )

    updated_fields = mapping_update.model_dump(exclude_unset=True)
    logger.info(f"Updating fields: {updated_fields}")
    for field, value in updated_fields.items():
        setattr(db_mapping, field, value)

    try:
        db.commit()
        db.refresh(db_mapping)
        logger.info(f"Successfully updated UserOutlet Mapping with ID {mapping_id}")
    except Exception as e:
        logger.error(f"Failed to update UserOutlet Mapping ID {mapping_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating UserOutlet Mapping"
        )

    return db_mapping

@router.delete("/user-outlet-mappings/{mapping_id}", status_code=200)
async def delete_user_outlet_mapping(
    mapping_id: int,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
    ):
    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    # Only verify request for non-internal clients
    if not is_internal_client:
        try:
            verify_request(
                client_id=current_session.client_id, 
                user_outlet_mapping_id=mapping_id,
                db=db
            )
            logger.info(f"Request verification successful for client {current_session.client_id}")
        except Exception as e:
            logger.error(f"Request verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to update UserOutlet Mapping"
            )
            
    try:
        logger.info(f"Attempting to delete UserOutlet Mapping with ID {mapping_id}")
        db_mapping = db.query(models.UserOutlet).filter(models.UserOutlet.id == mapping_id).first()

        if not db_mapping:
            logger.warning(f"UserOutlet Mapping with ID {mapping_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"UserOutlet Mapping with ID {mapping_id} not found"
            )

        db.delete(db_mapping)
        db.commit()
        logger.info(f"Successfully deleted UserOutlet Mapping with ID {mapping_id}")
        return JSONResponse(
            content={"message": f"UserOutlet Mapping with ID {mapping_id} successfully deleted"},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error occurred while deleting UserOutlet Mapping ID {mapping_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the UserOutlet Mapping"
        )
