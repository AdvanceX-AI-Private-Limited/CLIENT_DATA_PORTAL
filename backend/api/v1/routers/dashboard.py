from fastapi import APIRouter
import json
import time
from pydantic import BaseModel   # <-- import BaseModel

router = APIRouter() 

class RequestData(BaseModel):
    name: str = "World"

@router.get("/home")
async def dashboard():
    return {"status": "ok", "message": "Dashboard operational"}

@router.get("/test2")
async def test(name: str = "World"):
    # data = None
    # with open(r"C:\Users\Coreitez\Downloads\users.json", "r") as file:
        
    #     data = json.load(file)
    #     print(data)
    time.sleep(2)
    data = {
        "request": "get",
        "response": {
            "status": 200,
            "message": "Success",
            "data": {
                "name": f"{name}",
                "age": 30,
                "city": "New York"
            }
        }
    }
    return data


@router.post("/test")
async def test(request: RequestData):
    return {"name": request.name, "request": "post"}