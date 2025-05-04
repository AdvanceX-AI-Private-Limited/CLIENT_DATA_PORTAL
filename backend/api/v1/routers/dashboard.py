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
    'session': '.eJxdkG-PojAQh78K6WtFUcHFV8exK-i5q-geCpcNKVCh2lKgrfgnfvfDnJdc7tVkkpnnN_PcQLQnkOeIg8mvG1BEW0AD6wIXGeiAgEmFSi4UwjIFF4pgCkwSxLkicsyVEmZIBV_3rw6ISlRTWKCiJYhaog5IapS2LYakZd9AQnDbRTgFE6ANTXNk6Npw3C0OEp-OMB_Jfl9WWlwcykE1GkuSYkpkTFVYllzNGMsIkhzVCStEy1ETRtv7nlCO2rA2GDhLe7PadY3qitauyL3TEDqO6xpy7k8d_J2PX6J2q0b7GvE8EuyICjApJCEdwBNWPiyAXIiST3q9pmmeubDE_BHYg1LkvccVuNgzFVGISYt7YsAFDkwV9q0wOH6Euacl5_XImuJtgxNx9XVq1rErzvFbyYb4Mgvz2gjL2cGm4Xb1OX0zwu3rLnLm637wetykfuDm-tXybbh4-fDsYEWq6_kdGYa9jPSTt_ODPOka8XrBnQ2tLuHsOmxO0TlczvbL5ehkcNN0zUUN5w62siowJcH-OnFw5Gm1R_UsptDOgh-W_3NjrYPN1HOd3eAdM3GdbT9Lk_jpQQvktkn3M9vqa2P976ORrPE_ltjDyeB_UX-U3DvgIaudhpxAqlJ8gd9geoJFgs4qxOD-G19l3Ds.aBd0qw.cLM6vkvN8aTMdBCZfTAABvYqWDQ',
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