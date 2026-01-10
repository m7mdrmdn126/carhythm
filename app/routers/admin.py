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
async def dashboard(request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Admin dashboard."""
    from ..models import Page, Question, StudentResponse, Feedback
    from ..models.question_pool import QuestionPool
    
    # Get statistics
    stats = {
        "total_pages": db.query(Page).count(),
        "total_questions": db.query(Question).count(),
        "total_responses": db.query(StudentResponse).count(),
        "total_pool_questions": db.query(QuestionPool).count(),
        "total_feedbacks": db.query(Feedback).count()
    }
    
    return templates.TemplateResponse(
        "admin/dashboard.html", 
        {"request": request, "admin": admin, "stats": stats}
    )

@router.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Analytics dashboard with charts and insights."""
    from ..models import StudentResponse
    from ..services import response_service
    
    statistics = response_service.get_response_statistics(db)
    recent_responses = db.query(StudentResponse).order_by(StudentResponse.created_at.desc()).limit(20).all()
    
    # Calculate average rating from feedbacks
    from ..models import Feedback
    from sqlalchemy import func
    avg_rating = db.query(func.avg(Feedback.rating)).filter(
        Feedback.rating.isnot(None)
    ).scalar()
    
    return templates.TemplateResponse(
        "admin/analytics.html",
        {
            "request": request,
            "admin": admin,
            "statistics": statistics,
            "recent_responses": recent_responses,
            "avg_rating": round(avg_rating, 1) if avg_rating else None,
            "format_datetime": lambda dt: dt.strftime('%b %d, %Y %I:%M %p') if dt else ''
        }
    )

@router.get("/analytics/data")
async def analytics_data(db: Session = Depends(get_db), admin=Depends(require_admin)):
    """API endpoint for analytics chart data."""
    from ..models import StudentResponse as Response, AssessmentScore
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Get response trend data (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    response_trend = db.query(
        func.date(Response.created_at).label('date'),
        func.count(Response.id).label('count')
    ).filter(
        Response.created_at >= thirty_days_ago
    ).group_by(
        func.date(Response.created_at)
    ).all()
    
    # Get completion statistics
    total_responses = db.query(Response).count()
    completed = db.query(Response).filter(Response.is_completed == True).count()
    in_progress = total_responses - completed
    completion_rate = (completed / total_responses * 100) if total_responses > 0 else 0
    
    # Get RIASEC distribution from completed assessments
    riasec_scores = db.query(AssessmentScore).filter(
        AssessmentScore.riasec_realistic.isnot(None)
    ).all()
    
    riasec_distribution = {
        'Realistic': sum(s.riasec_realistic or 0 for s in riasec_scores) / len(riasec_scores) if riasec_scores else 0,
        'Investigative': sum(s.riasec_investigative or 0 for s in riasec_scores) / len(riasec_scores) if riasec_scores else 0,
        'Artistic': sum(s.riasec_artistic or 0 for s in riasec_scores) / len(riasec_scores) if riasec_scores else 0,
        'Social': sum(s.riasec_social or 0 for s in riasec_scores) / len(riasec_scores) if riasec_scores else 0,
        'Enterprising': sum(s.riasec_enterprising or 0 for s in riasec_scores) / len(riasec_scores) if riasec_scores else 0,
        'Conventional': sum(s.riasec_conventional or 0 for s in riasec_scores) / len(riasec_scores) if riasec_scores else 0,
    }
    
    # Get recent activity
    recent_responses = db.query(Response).order_by(Response.created_at.desc()).limit(10).all()
    recent_activity = [
        {
            'id': r.id,
            'name': r.student_name or 'Anonymous',
            'email': r.student_email or 'N/A',
            'status': 'Completed' if r.is_completed else 'In Progress',
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M')
        }
        for r in recent_responses
    ]
    
    return {
        "response_trend": [{"date": str(r.date), "count": r.count} for r in response_trend],
        "completion_stats": {
            "completed": completed,
            "in_progress": in_progress,
            "completion_rate": round(completion_rate, 1)
        },
        "riasec_distribution": riasec_distribution,
        "recent_activity": recent_activity
    }

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Admin settings page."""
    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "admin": admin}
    )

@router.post("/settings/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Change admin password."""
    from ..utils.security import verify_password, get_password_hash
    
    # Verify current password
    if not verify_password(current_password, admin.password_hash):
        return templates.TemplateResponse(
            "admin/settings.html",
            {"request": request, "admin": admin, "error": "Current password is incorrect"}
        )
    
    # Verify new passwords match
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "admin/settings.html",
            {"request": request, "admin": admin, "error": "New passwords do not match"}
        )
    
    # Update password
    admin.password_hash = get_password_hash(new_password)
    db.commit()
    
    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "admin": admin, "success": "Password updated successfully"}
    )