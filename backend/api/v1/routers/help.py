from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
def login_ui_page(request: Request):
    return templates.TemplateResponse("loginflow.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
def register_ui_page(request: Request):
    return templates.TemplateResponse("registerflow.html", {"request": request})

@router.get("/otp", response_class=HTMLResponse)
def otp_ui_page(request: Request):
    return templates.TemplateResponse("registerflow.html", {"request": request})
