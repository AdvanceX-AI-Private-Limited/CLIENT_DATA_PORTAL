from fastapi import APIRouter


router = APIRouter() 

# Health check endpoint
@router.get("/dashboard")
async def dashboard():
    return {"status": "ok", "message": "Dashboard operational"}