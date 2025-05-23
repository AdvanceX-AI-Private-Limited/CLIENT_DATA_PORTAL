
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..schemas import schemas
from ..database import models
from logger import create_logger

# Initialize logger
logger = create_logger(__name__)


router = APIRouter() 

#______________________________________ Brand routes ______________________________________
@router.post("/brands/", response_model=List[schemas.DisplayBrand])
async def create_brand(
    brands: List[schemas.BrandCreate],
    db: Session = Depends(get_db) 
):
    logger.info("Received request to create brands: %s", brands)
    created_brands = []

    for brand in brands:
        # Check if client exists
        existing_client = db.query(models.Client).filter(
            (models.Client.id == brand.clientid)
        ).first()
        if not existing_client:
            logger.error("Client ID %s not found for brand '%s'", brand.client_id, brand.brandname)
            raise HTTPException(
                status_code=400,
                detail="Unknown client ID passed"
            )

        # Check if brand already exists
        db_brand = db.query(models.Client).filter(
            (models.Brand.brandname == brand.brandname)
        ).first()
        if db_brand:
            logger.warning("Brand with name '%s' already exists", brand.brandname)
            raise HTTPException(
                status_code=400,
                detail="Brand already registered"
            )
        
        db_brand = models.Brand(
            brandname=brand.brandname,
            client_id=brand.client_id 
        )
        db.add(db_brand)
        db.commit()
        db.refresh(db_brand)
        logger.info(
            "Successfully created brand '%s' with ID %s under client ID %s",
            db_brand.brandname, db_brand.id, db_brand.client_id
        )
        created_brands.append(db_brand)

    if not created_brands:
        logger.error("No brands were created. All entries were duplicates or had invalid client IDs.")
        raise HTTPException(
            status_code=400, 
            detail="No brands were created. All were duplicates or had invalid client IDs."
        )

    return created_brands

@router.get("/brands/", response_model=List[schemas.DisplayBrand])
async def read_brands(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    logger.info("Received request to fetch brands:%s - skip:%s - end:%s", 
                brands, skip, limit)
    query = db.query(models.Brand)
    brands = query.offset(skip).limit(limit).all()
    if not brands:
        logger.error("No brands were found. Invalid parameters passed.")
        raise HTTPException(
            status_code=400, 
            detail="No brands were found. Invalid parameters passed."
        )

    logger.info("Successfully fetched brands '%s' with ID %s under client ID %s",
        brands, skip, limit
    )
    return brands

@router.get("/brands/client/{client_id}", response_model=List[schemas.DisplayBrand])
async def read_brand_of_clients(
    client_id: int, 
    db: Session = Depends(get_db)
):
    logger.info("Received request to fetch brands for client_id:%s", 
                client_id)
    db_brand = db.query(models.Brand).filter(models.Brand.client_id == client_id).all()
    if db_brand is None:
        raise HTTPException(status_code=404, detail="Outlets not found for client_id")
    
    if not db_brand:
        logger.error("No brands found for passed client id. Invalid parameters passed.")
        raise HTTPException(
            status_code=400, 
            detail="No brands found for passed client id"
        )
    
    logger.info("Successfully fetched brands for client_id:%s", 
                client_id)  
    return db_brand

@router.get("/brands/{brand_id}", response_model=schemas.DisplayBrand)
async def read_brand(
    brand_id: int, 
    db: Session = Depends(get_db)
):
    logger.info("Received request to fetch details for brand_id:%s", 
                brand_id)
    db_brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()

    if db_brand is None:
        logger.error("No details found for passed brand id. Invalid parameters passed.")
        raise HTTPException(status_code=404, 
                            detail="Details not found for brand_id")
    
    logger.info("Successfully fetched details for brand_id:%s", 
                brand_id)  
    return db_brand


#______________________________________ Outlet routes ______________________________________
@router.post("/outlets/", response_model=List[schemas.DisplayOutlet])
async def create_outlet(
    outlets: List[schemas.OutletCreate], 
    db: Session = Depends(get_db)
):
    created_outlets = []

    for outlet in outlets:
        # Check if client exists
        existing_client = db.query(models.Client).filter(
            (models.Client.id == outlet.clientid)
        ).first()
        if not existing_client:
            raise HTTPException(
                status_code=400,
                detail="Unknown client ID passed"
            )
        
        # Check if brand already exists
        existing_outlet = db.query(models.Outlet).filter(
            (models.Outlet.aggregator == outlet.aggregator) &
            (models.Outlet.resid == outlet.resid)
        ).first()
        if existing_outlet:
            raise HTTPException(
                status_code=400,
                detail="Res ID already registered"
            )
        
        # Get brand using brand_id
        db_brand = db.query(models.Brand).filter(models.Brand.id == outlet.brandid).first()
        if not db_brand:
            raise HTTPException(
                status_code=404,
                detail="Brand not found"
            )
            
        # Generate brand abbreviation
        brand_name_words = (db_brand.brandname.strip()).split()
        if len(brand_name_words) > 1:
            # Take first letter of each word for abbreviation
            abbreviation = ''.join([word[0].upper() for word in brand_name_words if word])
        else:
            # Use full brand name if single word
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
            brand_id=outlet.brandid
        )
        db.add(db_outlet)
        db.commit()
        db.refresh(db_outlet)
        created_outlets.append(db_outlet)

    if not created_outlets:
        raise HTTPException(status_code=400, detail="No outlets were created. All were duplicates.")

    return created_outlets

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
@router.post("/users/", response_model=List[schemas.DisplayUser])
async def create_users(
    users: List[schemas.UserCreate], 
    db: Session = Depends(get_db)
):
    
    created_users = []

    for user in users:
        # Check if client exists
        existing_client = db.query(models.Client).filter(
            (models.Client.id == user.clientid)
        ).first()
        if not existing_client:
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
        db.commit()
        db.refresh(db_user)
        created_users.append(db_user)

    if not created_users:
        raise HTTPException(status_code=400, detail="No users were created. All were duplicates.")

    return created_users


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

