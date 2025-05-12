from fastapi import APIRouter
import json
import time
from pydantic import BaseModel   # <-- import BaseModel
import requests
import pandas as pd
from asyncio import sleep
import httpx
import math
from typing import List, Dict, Any

router = APIRouter() 

class User(BaseModel):
    name: str
    number: str

class MappingDataInner(BaseModel):
    red_id: List[int]
    users: List[User]
    action: str

class MappingData(BaseModel):
    data: MappingDataInner
    
class RequestData(BaseModel):
    name: str = "World"

@router.get("/home")
async def dashboard():
    return {"status": "ok", "message": "Dashboard operational"}

cookies = {
    '_ga': 'GA1.1.312283043.1742895003',
    '_ga_2WR26M0758': 'GS1.1.1745841255.5.1.1745842214.0.0.0',
    'session': '.eJxdkGuvmkAQhv8K2c-KCHj9VC89Uq3xICpoc0LGdYVF2AWWBS_xvxdTmzT9NJlk5nlnngfyzzGIkAg0_PVASlEXVEHOKAtQA-25VBIpCiXmgUKZUnAFMCZCKEVIhZJCQFT09fxqID8leQKMsJpQ5JI0EM7JqW4pxDX7gXBM686nJzREbWMwMLudttFrskjS8gKhKTVNZu0ji1I9M3syPtEklsdEhTQVasB5EBMpSI45K2qOinlS3_eGClKH1cFotpo4n16zm93J2ipCuzRgNrOsrpzvPmZ0LHp9v97KyTknIvQLfiEMDZmM4wYSmKcvCygsilQMW62qqt65kFLxCmyBLMLW6wrKzlwlCdC4xr0x6Ab6QAVt5JpecY1oc_SDO4fTGvDV0BYGt92V4zQj27t93kdmNO3czt_D9DDWJes745vt6tv-RADRx0awvQYOa_NNpNke_Zl5m4N3X97d8XpmLdn2GB0yFl66NszXRnbdruZm2CdL192J7uCA55nBd6vYKTmedpoj11otQm3slkeYltjgZnCzYLFcwyTYL0YH2xmt986Hbc08fUkrubCrzbx07-list0lJ_CX2Nbavc7fR32Z038s8ZcT_X9Rf5Q8G-glq54GEUOiJvQG3-BUAsPkqgJFz9939dtR.aB2utA.vYfFTIXz52xt8ERHnyOPNl0POa0',
}

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
    print("Test API")
    await sleep(5)
    return {"name": request.name, "request": "post"}

# data = pd.read_csv(r"C:\Users\Coreitez\Codes\adx\CLIENT_DATA_PORTAL\backend\mapped_outlets_new.csv")

def clean_obj(obj):
    """Recursively handle NaN, inf, -inf in dicts/lists for JSON serialization."""
    if isinstance(obj, dict):
        return {k: clean_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_obj(i) for i in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    # Handle pd.NA (nullable integer etc.)
    try:
        import pandas as pd
        if pd.isna(obj):
            return None
    except Exception:
        pass
    return obj

@router.get("/outlets-data")
async def mapped_outlets_data():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://data.advancex.ai/mapper/upload/get-table-data/Outlets',
            cookies=cookies,
            timeout= None,
        )
        # print(response.status_code)
        # print(response.text)
        data = response.json()
    data = response.json()
    return data

@router.get("/services-data")
async def mapped_services_data():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://data.advancex.ai/mapper/upload/get-table-data/Services',
            cookies=cookies,
            timeout= None,
        )
        # print(response.status_code)
        # print(response.text)
        data = response.json()
    data = response.json()
    return data

@router.get("/users-data")
async def mapped_users_data():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://data.advancex.ai/mapper/upload/get-table-data/Users',
            cookies=cookies,
            timeout= None,
        )
        print(response.status_code)
        # print(response.text)
        data = response.json()
    data = response.json()
    # await sleep(20)
    return data

@router.get("/mapped-users-data")
async def mapped_users_data():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://data.advancex.ai/api/mapper/outlets-to-users-get-mapped-users',
            cookies=cookies,
            timeout= None,
        )
        print(response.status_code)
        # print(response.text)
        data = response.json()
    data = response.json()
    return data

@router.get("/mapped-users-to-services")
async def mapped_users_to_services():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://data.advancex.ai/api/mapper/users-to-services-get-mapped-services',
            cookies=cookies,
            timeout= None,
        )
        print(response.status_code)
        # print(response.text)
        data = response.json()
    data = response.json()
    return data

@router.get("/mapped-outlets-to-services")
async def mapped_outlet_to_services():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://data.advancex.ai/api/mapper/outlets-to-services-get-mapped-services',
            cookies=cookies,
            timeout= None,
        )
        print(response.status_code)
        # print(response.text)
        data = response.json()
    data = response.json()
    return data

# @router.get("/mapped-users-data")
# async def mapped_users_data():
#     data = pd.read_csv(r"C:\Users\Coreitez\Downloads\ZOMATO_DISCOUNTS_1737010350 (1).csv")
#     data = data.where(pd.notnull(data), None)
#     data = data.to_dict(orient='records')
#     print("DOne")
#     return clean_obj(data)


# @router.post("/map-users-to-outlets")
# async def map_users_to_outlets(request):
#     print("Mapped Users to Outlets")
#     await sleep(3)
#     print(request)
#     return {"status": "ok", "message": "Mapped Users to Outlets"}

@router.post("/map-users-to-outlets")
async def map_users_to_outlets(request: MappingData):
    print("Mapped Users to Outlets")
    print(request.data.dict())
    await sleep(3)
    return {"message": "Mapped Users to Outlets", "request": "post"}