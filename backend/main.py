import uvicorn
from contextlib import asynccontextmanager
from logger import create_logger
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from api.v1.database import models
from api.v1.database.database import engine, test_connection, get_database_info, create_tables
from api.v1.routers.auth import get_current_active_user
from api.v1.routers import auth, access, admin, automation, dashboard, help

logger = create_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    try:
        logger.info("Starting FastAPI application startup...")
        
        # Test database connection
        logger.info("Testing database connection...")
        if test_connection():
            logger.info("Database connection verified successfully")
            
            # Get and log database info
            db_info = get_database_info()
            logger.info(f"Database info: {db_info}")
            
            # Create tables if they don't exist
            logger.info("Creating database tables if they don't exist...")
            if create_tables():
                logger.info("Database tables created/verified successfully")
                
                # Also create tables using the models Base (backup method)
                try:
                    models.Base.metadata.create_all(bind=engine)
                    logger.info("Models-based table creation completed")
                except Exception as e:
                    logger.warning(f"Models-based table creation warning: {e}")
            else:
                logger.warning("Some issues occurred while creating tables")
                
        else:
            logger.error("Database connection failed during startup")
            raise Exception("Database connection failed - cannot start application")
            
        logger.info("Application startup completed successfully")
            
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise e

    yield  # Application runs here
    
    # Cleanup after app shutdown
    logger.info("Application shutting down...")
    try:
        engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Application shutdown completed")

# Initialize FastAPI application with lifespan
logger.info("Initializing FastAPI application...")
app = FastAPI(
    title="Client Data Portal",
    description="API for getting data for Data Portal",
    version="1.0.0",
    # terms_of_service="",
    # contact={
    #     "name": "Support Team",
    #     "url": "",
    #     "email": "dontaskrahul@advancex.ai"
    # },
    # license_info={
    #     "name": "MIT",
    #     "url": "https://opensource.org/licenses/MIT"
    # },
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set up timezone
protected_router = APIRouter(dependencies=[Depends(get_current_active_user)])
IST = timezone(timedelta(hours=5, minutes=30))
logger.debug(f"Timezone set to IST: {IST}")

# Configure CORS
logger.info("Configuring CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured")

# Health check endpoint
@app.get("/", include_in_schema=False)
async def root():
    logger.info("Health check endpoint accessed")
    return {
        "status": "ok", 
        "message": "Service operational",
        "timestamp": datetime.now(IST).isoformat(),
        "version": "1.0.0"
    }

# Database health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check():
    """Comprehensive health check including database connectivity"""
    logger.info("Health check with database connectivity accessed")
    
    # Test database connection
    db_status = "connected" if test_connection() else "disconnected"
    db_info = get_database_info() if db_status == "connected" else {}
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "message": "All systems operational" if db_status == "connected" else "Database connection issues",
        "timestamp": datetime.now(IST).isoformat(),
        "database": {
            "status": db_status,
            "info": db_info
        },
        "version": "1.0.0"
    }

# Database info endpoint
@app.get("/db-info", include_in_schema=False)
async def database_info():
    """Get detailed database information"""
    logger.info("Database info endpoint accessed")
    return {
        "timestamp": datetime.now(IST).isoformat(),
        "database_info": get_database_info()
    }

# Main router for API version 1
logger.info("Setting up API version 1 router...")
api_v1_router = APIRouter(prefix="/api/v1")

# Include all sub-routers under the versioned router
logger.info("Including authentication router...")
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

logger.info("Including administration router...")
api_v1_router.include_router(admin.router, prefix="/admin", tags=["Administration"])

logger.info("Including access control router...")
api_v1_router.include_router(access.router, prefix="/access", tags=["Access Control"])

logger.info("Including automation router...")
api_v1_router.include_router(automation.router, prefix="/automation", tags=["Automation"])

logger.info("Including dashboard router...")
api_v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

logger.info("Including support router...")
api_v1_router.include_router(help.router, prefix="/help", tags=["Support"])

# Include all the above routers in main app
logger.info("Mounting version 1 router to main application...")
app.include_router(api_v1_router)

if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    logger.info(f"Server will run on: localhost:8000")
    logger.info(f"API documentation available at: /docs and /redoc")
    logger.info(f"Health check available at: /health")
    logger.info(f"Database info available at: /db-info")
    
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        log_level="info",
    )