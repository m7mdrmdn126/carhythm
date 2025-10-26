from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..models import get_db
from ..schemas import AdminLogin
from ..services.auth import login_admin, get_admin_by_username
from ..utils.security import verify_token
from typing import Optional

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

def get_current_admin(request: Request, db: Session = Depends(get_db)):
    """Get current authenticated admin from session."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    username = verify_token(token)
    if not username:
        return None
    
    admin = get_admin_by_username(db, username)
    return admin

def require_admin(request: Request, db: Session = Depends(get_db)):
    """Dependency to require admin authentication."""
    admin = get_current_admin(request, db)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return admin

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display admin login page."""
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process admin login."""
    login_data = AdminLogin(username=username, password=password)
    access_token = login_admin(db, login_data)
    
    if not access_token:
        return templates.TemplateResponse(
            "admin/login.html", 
            {"request": request, "error": "Invalid username or password"}
        )
    
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        samesite="lax"
    )
    return response

@router.get("/logout")
async def logout(request: Request):
    """Logout admin user."""
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("access_token")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, admin=Depends(require_admin)):
    """Admin dashboard."""
    return templates.TemplateResponse(
        "admin/dashboard.html", 
        {"request": request, "admin": admin}
    )