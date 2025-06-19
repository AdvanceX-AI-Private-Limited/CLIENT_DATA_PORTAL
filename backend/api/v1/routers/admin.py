
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .auth import get_current_session
from ..database.database import get_db
from ..schemas import schemas
from ..database import models
from logger import create_logger

# Initialize logger
logger = create_logger(__name__)


router = APIRouter() 
INTERNAL_CLIENT_IDS = {3}

def verify_request(client_id: int, 
                   db: Session, 
                   outlet_id: int = None, 
                   brand_id: int = None,
                   user_id: int = None,
                   service_id: int = None):
    
    if outlet_id is not None:
        outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id).first()
        if outlet:
            if outlet.client_id != client_id:
                raise HTTPException(status_code=403, detail="Forbidden: You don't own this outlet")
        else:
            raise HTTPException(status_code=404, detail="Outlet not found")
    
    elif brand_id is not None:
        brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
        if brand:
            if brand.client_id != client_id:
                raise HTTPException(status_code=403, detail="Forbidden: You don't own this brand")
        else:
            raise HTTPException(status_code=404, detail="Brand not found")
        
    elif user_id is not None:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            if user.client_id != client_id:
                raise HTTPException(status_code=403, detail="Forbidden: You don't own this brand")
        else:
            raise HTTPException(status_code=404, detail="User not found")

#______________________________________ Brand routes ______________________________________
@router.get("/brands/", response_model=List[schemas.DisplayBrand])
async def get_brands(
    params: schemas.BrandQueryParams = Depends(),
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    query = db.query(models.Brand)

    # Filter by brand_id (single brand)
    if params.brand_id is not None:
        brand = query.filter(models.Brand.id == params.brand_id).first()
        if brand is None:
            raise HTTPException(status_code=404, detail="Brand not found")
        return [brand]

    # Filter by client_id
    if params.client_id is not None:
        query = query.filter(models.Brand.client_id == params.client_id)

    # Apply pagination
    brands = query.offset(params.skip).limit(params.limit).all()
    return brands

@router.put("/brands/{brand_id}", response_model=schemas.DisplayBrand)
async def update_brand(
    brand_id: int,
    brand_update: schemas.UpdateBrand,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    verify_request(client_id=current_session.client_id, 
                   brand_id=brand_id,
                   db=db)
    
    logger.info(f"Attempting to update brand with ID {brand_id}")
    db_brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()

    if not db_brand:
        logger.warning(f"Brand with ID {brand_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Brand with ID {brand_id} not found"
        )

    updated_fields = brand_update.model_dump(exclude_unset=True)
    for field, value in updated_fields.items():
        setattr(db_brand, field, value)

    db.commit()
    db.refresh(db_brand)
    logger.info(f"Successfully updated brand with ID {brand_id}")
    return db_brand

@router.delete("/brands/{brand_id}", status_code=200)
async def delete_brand(
    brand_id: int,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    verify_request(client_id=current_session.client_id, 
                   brand_id=brand_id,
                   db=db)
    logger.info(f"Attempting to delete brand with ID {brand_id}")
    db_brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()

    if not db_brand:
        logger.warning(f"Brand with ID {brand_id} not found for deletion")
        raise HTTPException(
            status_code=404,
            detail=f"Brand with ID {brand_id} not found"
        )

    db.delete(db_brand)
    db.commit()
    logger.info(f"Successfully deleted Brand with ID {brand_id}")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message":  f"Brand with ID {brand_id} successfully deleted"
        }
    )


#______________________________________ Outlet routes ______________________________________
@router.post("/outlets/", response_model=List[schemas.DisplayOutlet])
async def create_outlet(
    outlets: List[schemas.OutletCreate], 
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):  
    logger.info(f"Received request to create {len(outlets)} outlet(s) by client ID: {current_session.client_id}")
    
    created_outlets = []

    for outlet in outlets:
        logger.info(f"Processing outlet: resid={outlet.resid}, aggregator={outlet.aggregator}")

        # Check if client exists
        existing_client = db.query(models.Client).filter(
            (models.Client.id == outlet.clientid)
        ).first()
        if not existing_client:
            logger.warning(f"Unknown client ID: {outlet.clientid}")
            raise HTTPException(
                status_code=400,
                detail="Unknown client ID passed"
            )
        
        # Check if outlet already exists
        existing_outlet = db.query(models.Outlet).filter(
            (models.Outlet.aggregator == outlet.aggregator) &
            (models.Outlet.resid == outlet.resid)
        ).first()
        if existing_outlet:
            logger.warning(f"Duplicate outlet found: resid={outlet.resid}, aggregator={outlet.aggregator}")
            raise HTTPException(
                status_code=400,
                detail="Res ID already registered"
            )
        
        # Get brand using brand_id
        db_brand = db.query(models.Brand).filter(models.Brand.client_id == outlet.clientid).first()
        if not db_brand:
            logger.error(f"Brand not found for client ID: {outlet.clientid}")
            raise HTTPException(
                status_code=404,
                detail="Brand not found"
            )
            
        # Generate brand abbreviation
        brand_name_words = (db_brand.brandname.strip()).split()
        if len(brand_name_words) > 1:
            abbreviation = ''.join([word[0].upper() for word in brand_name_words if word])
        else:
            abbreviation = db_brand.brandname

        # Create res_shortcode
        res_shortcode = f"{abbreviation} - {outlet.subzone}"

        db_outlet = models.Outlet(
            aggregator=outlet.aggregator,
            resid=outlet.resid,
            subzone=outlet.subzone,
            resshortcode=res_shortcode,
            city=outlet.city,
            outletnumber=outlet.outletnumber,
            is_active=outlet.is_active,
            client_id=outlet.clientid,
            brand_id=db_brand.id
        )

        db.add(db_outlet)
        try:
            db.commit()
            db.refresh(db_outlet)
            created_outlets.append(db_outlet)
            logger.info(f"Successfully created outlet: resid={db_outlet.resid}, shortcode={db_outlet.resshortcode}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create outlet: resid={outlet.resid}, error={str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create outlet due to internal error")

    if not created_outlets:
        logger.warning("No new outlets were created. All were duplicates or failed.")
        raise HTTPException(status_code=400, detail="No outlets were created. All were duplicates.")

    logger.info(f"Successfully created {len(created_outlets)} outlet(s)")
    return created_outlets

@router.get("/outlets/", response_model=List[schemas.DisplayOutlet])
async def get_outlets(
    params: schemas.OutletQueryParams = Depends(),
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to get outlets with params : {params}")

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

    query = db.query(models.Outlet)

    # Filter by brand_id (single brand)
    if params.outlet_id is not None:
        outlet = query.filter(models.Outlet.id == params.outlet_id).first()
        if outlet is None:
            raise HTTPException(status_code=404, detail="Outlet not found")
        return [outlet]

    if not is_internal_client:
    # Filter by client_id
        if params.client_id is not None:
            query = query.filter(models.Outlet.client_id == params.client_id)

    if params.status == models.StatusEnum.active:
        query = query.filter(models.Outlet.is_active == True)
    elif params.status == models.StatusEnum.inactive:
        query = query.filter(models.Outlet.is_active == False)

    # Apply pagination
    outlets = query.offset(params.skip).limit(params.limit).all()
    return outlets

@router.put("/outlets/{outlet_id}", response_model=schemas.DisplayOutlet)
async def update_outlet(
    outlet_id: int,
    outlet_update: schemas.UpdateOutlet,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to update outlet with ID {outlet_id}")

    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    logger.info(f"Client ID {current_session.client_id} is_internal_client={is_internal_client}")

    if not is_internal_client:
        is_client_same = (
            hasattr(current_session, "client_id") and 
            hasattr(outlet_update, "client_id") and 
            current_session.client_id == outlet_update.client_id
        )
        logger.info(f"Client ID match check: {is_client_same}")

        if is_client_same:
            try:
                verify_request(
                    client_id=current_session.client_id, 
                    outlet_id=outlet_id,
                    db=db
                )
                logger.info(f"Request verification successful for client {current_session.client_id}")
            except Exception as e:
                logger.error(f"Request verification failed: {str(e)}")
                raise HTTPException(
                    status_code=403,
                    detail="Unauthorized access to update outlet"
                )

    logger.info(f"Fetching outlet with ID {outlet_id}")
    db_outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id).first()

    if not db_outlet:
        logger.warning(f"Outlet with ID {outlet_id} not found in database")
        raise HTTPException(
            status_code=404,
            detail=f"Outlet with ID {outlet_id} not found"
        )

    logger.info(f"Checking for duplicates: aggregator={outlet_update.aggregator}, resid={outlet_update.resid}")
    existing = db.query(models.Outlet).filter(
        models.Outlet.aggregator == outlet_update.aggregator,
        models.Outlet.resid == outlet_update.resid,
        models.Outlet.id != outlet_id  # exclude current record
    ).first()
    if existing:
        logger.warning("Duplicate outlet found with same aggregator and resid")
        raise HTTPException(
            status_code=400,
            detail="Another outlet with the same aggregator and resid already exists."
        )

    updated_fields = outlet_update.model_dump(exclude_unset=True)
    logger.info(f"Updating fields: {updated_fields}")
    for field, value in updated_fields.items():
        setattr(db_outlet, field, value)

    try:
        db.commit()
        db.refresh(db_outlet)
        logger.info(f"Successfully updated outlet with ID {outlet_id}")
    except Exception as e:
        logger.error(f"Failed to update outlet ID {outlet_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating outlet"
        )

    return db_outlet

@router.delete("/outlets/{outlet_id}", status_code=200)
async def delete_outlet(
    outlet_id: int,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    logger.info(f"Delete request received for outlet ID {outlet_id} by client ID {current_session.client_id}")

    if not is_internal_client:
        try:
            verify_request(
                client_id=current_session.client_id, 
                outlet_id=outlet_id,
                db=db
            )
            logger.info(f"Request verified for client ID {current_session.client_id} and outlet ID {outlet_id}")
        except Exception as e:
            logger.warning(f"Request verification failed for outlet ID {outlet_id}: {str(e)}")
            raise
            
    try:
        db_outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id).first()
        if not db_outlet:
            logger.warning(f"Outlet with ID {outlet_id} not found for deletion")
            raise HTTPException(
                status_code=404,
                detail=f"Outlet with ID {outlet_id} not found"
            )

        db.delete(db_outlet)
        db.commit()
        logger.info(f"Successfully deleted outlet with ID {outlet_id}")
        return JSONResponse(
            content={"message": f"Outlet with ID {outlet_id} successfully deleted"},
            status_code=200
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error occurred while deleting outlet ID {outlet_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting the outlet"
        )


#______________________________________ User routes ______________________________________
@router.post("/users/", response_model=List[schemas.DisplayUser])
async def create_users(
    users: List[schemas.UserCreate], 
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to create {len(users)} user(s) by client ID: {current_session.client_id}")
    
    created_users = []

    for user in users:
        logger.info(f"Processing user: username={user.username}, email={user.useremail}, number={user.usernumber}")

        # Check if client exists
        existing_client = db.query(models.Client).filter(
            (models.Client.id == user.clientid)
        ).first()
        if not existing_client:
            logger.warning(f"Unknown client ID: {user.clientid}")
            raise HTTPException(
                status_code=400,
                detail="Unknown client ID passed"
            )

        # Check if user already exists
        existing_user = db.query(models.User).filter(
            (models.User.usernumber == user.usernumber) &
            (models.User.useremail == user.useremail)
        ).first()
        if existing_user:
            logger.warning(f"Duplicate user found: email={user.useremail}, number={user.usernumber}")
            raise HTTPException(
                status_code=400,
                detail="User is already registered"
            )

        db_user = models.User(
            username=user.username,
            usernumber=user.usernumber,
            useremail=user.useremail,
            client_id=user.clientid
        )

        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)
            created_users.append(db_user)
            logger.info(f"Successfully created user: id={db_user.id}, email={db_user.useremail}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error while creating user {user.useremail}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create user due to internal error"
            )

    if not created_users:
        logger.warning("No users were created. All were duplicates or failed.")
        raise HTTPException(status_code=400, detail="No users were created. All were duplicates.")

    logger.info(f"Successfully created {len(created_users)} user(s)")
    return created_users

@router.get("/users/", response_model=List[schemas.DisplayUser])
async def read_users(
    params: schemas.UserQueryParams = Depends(),
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"User list request by client ID: {current_session.client_id} with params: {params.dict()}")

    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    if not is_internal_client:
        if params.user_id:
            try:
                verify_request(
                    client_id=current_session.client_id, 
                    user_id=params.user_id,
                    db=db
                )
                logger.info(f"Request verified for user ID {params.user_id} and client ID {current_session.client_id}")
            except Exception as e:
                logger.warning(f"Request verification failed for user ID {params.user_id}: {str(e)}")
                raise

    try:
        query = db.query(models.User)

        if not is_internal_client:
            if params.client_id is not None:
                logger.info(f"Filtering users for client ID {params.client_id}")
                query = query.filter(models.User.client_id == params.client_id)

        users = query.offset(params.skip).limit(params.limit).all()
        logger.info(f"Retrieved {len(users)} user(s) with skip={params.skip}, limit={params.limit}")

        return users

    except Exception as e:
        logger.error(f"Error while retrieving users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@router.put("/users/{user_id}", response_model=schemas.DisplayUser)
async def update_user(
    user_id: int,
    user_update: schemas.UpdateUser,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to update user with ID {user_id}")

    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    logger.info(f"Client ID {current_session.client_id} is_internal_client={is_internal_client}")

    if not is_internal_client:
        is_client_same = (
            hasattr(current_session, "client_id") and 
            hasattr(user_update, "client_id") and 
            current_session.client_id == user_update.client_id
        )
        logger.info(f"Client ID match check: {is_client_same}")

        if is_client_same:
            try:
                verify_request(
                    client_id=current_session.client_id, 
                    user_id=user_id,
                    db=db
                )
                logger.info(f"Request verification successful for client {current_session.client_id}")
            except Exception as e:
                logger.error(f"Request verification failed: {str(e)}")
                raise HTTPException(
                    status_code=403,
                    detail="Unauthorized access to update user"
                )

    logger.info(f"Fetching user with ID {user_id}")
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_user:
        logger.warning(f"User with ID {user_id} not found in database")
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )

    logger.info(f"Checking for duplicates: usernumber={user_update.usernumber}")
    existing = db.query(models.User).filter(
        models.User.usernumber == user_update.usernumber,
        models.User.id != user_id  # exclude current record
    ).first()
    if existing:
        logger.warning("Duplicate user found with same aggregator and resid")
        raise HTTPException(
            status_code=400,
            detail="Another user with the same aggregator and resid already exists."
        )

    updated_fields = user_update.model_dump(exclude_unset=True)
    logger.info(f"Updating fields: {updated_fields}")
    for field, value in updated_fields.items():
        setattr(db_user, field, value)

    try:
        db.commit()
        db.refresh(db_user)
        logger.info(f"Successfully updated user with ID {user_id}")
    except Exception as e:
        logger.error(f"Failed to update user ID {user_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating user"
        )

    return db_user

@router.delete("/users/{user_id}", status_code=200)
async def delete_user(
    user_id: int,
    current_session = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    is_internal_client = current_session.client_id in INTERNAL_CLIENT_IDS
    # Only verify request for non-internal clients
    if not is_internal_client:
        try:
            verify_request(
                client_id=current_session.client_id, 
                user_id=user_id,
                db=db
            )
            logger.info(f"Request verification successful for client {current_session.client_id}")
        except Exception as e:
            logger.error(f"Request verification failed: {str(e)}")
            raise HTTPException(
                status_code=403,
                detail="Unauthorized access to update user"
            )
            
    logger.info(f"Attempting to delete user with ID {user_id}")
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_user:
        logger.warning(f"User with ID {user_id} not found for deletion")
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )

    db.delete(db_user)
    db.commit()
    logger.info(f"Successfully deleted user with ID {user_id}")
    return JSONResponse(
        content={"message": f"User with ID {user_id} successfully deleted"},
        status_code=200
    )


#______________________________________ Service routes ______________________________________
@router.post("/services/", response_model=schemas.DisplayService)
async def create_service(
    service: schemas.ServiceCreate, 
    db: Session = Depends(get_db)
):
    # Check if user service exists
    existing_service = db.query(models.Service).filter(
        (models.Service.servicename == service.servicename) &
        (models.Service.servicename == service.servicename)
    ).first()
    if existing_service:
        raise HTTPException(
            status_code=400,
            detail="Service is already registered"
        )
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

