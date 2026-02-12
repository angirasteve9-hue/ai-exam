from fastapi import APIRouter, Depends, HTTPException, status, Request, Form

from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from .. import models, database
from ..database import get_db
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "title": "Sign Up"})

@router.post("/signup")
def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Email already registered", "title": "Sign Up"})
    
    # In a real app, hash the password!
    new_user = models.User(email=email, hashed_password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto-login (set session cookie)
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="user_email", value=email)
    return response

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})

@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or user.hashed_password != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials", "title": "Login"})
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="user_email", value=email)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("user_email")
    return response
