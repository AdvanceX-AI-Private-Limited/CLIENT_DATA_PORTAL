import uvicorn
from logger import create_logger
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from api.v1.database import models
from api.v1.database.database import engine
from api.v1.routers.auth import get_current_active_user
from api.v1.routers import auth, access, admin, automation, dashboard, help


logger = create_logger()

# Initialize FastAPI application
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
)

logger.info("Creating database tables if they don't exist...")
models.Base.metadata.create_all(bind=engine)
logger.info("Database tables initialized successfully")

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
    return {"status": "ok", "message": "Service operational"}

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
    uvicorn.run(app,
                host="localhost",
                port=8000,
                )