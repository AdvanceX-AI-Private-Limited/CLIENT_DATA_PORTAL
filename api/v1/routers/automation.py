from fastapi import APIRouter


router = APIRouter() 

# Health check endpoint
@router.get("/home")
async def automation():
    return {"status": "ok", "message": "Automation operational"}