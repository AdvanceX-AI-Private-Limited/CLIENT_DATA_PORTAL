from fastapi import APIRouter


router = APIRouter() 

# Health check endpoint
@router.get("/home")
async def support():
    return {"status": "ok", "message": "Support operational"}