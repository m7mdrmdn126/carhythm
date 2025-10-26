from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# Import models and database setup
from .models import create_tables, get_db, Admin
from .utils.security import get_password_hash
from .routers.admin import router as admin_router
from .routers.admin_panel import router as admin_panel_router
from .routers.examination import router as examination_router
from .routers.question_pool import router as question_pool_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Career DNA Assessment", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Add custom Jinja2 filters
import json
def from_json(value):
    """Parse JSON string to Python object."""
    try:
        if value:
            return json.loads(value)
        return {}
    except (json.JSONDecodeError, TypeError):
        return {}

templates.env.filters["from_json"] = from_json

# Include routers
app.include_router(admin_router)
app.include_router(admin_panel_router)
app.include_router(examination_router)
app.include_router(question_pool_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database and create default admin user."""
    create_tables()
    
    # Create default admin if it doesn't exist
    db = next(get_db())
    admin_exists = db.query(Admin).filter(Admin.username == "admin").first()
    if not admin_exists:
        admin_user = Admin(
            username=os.getenv("ADMIN_USERNAME", "admin"),
            password_hash=get_password_hash(os.getenv("ADMIN_PASSWORD", "admin123"))
        )
        db.add(admin_user)
        db.commit()
    db.close()

@app.get("/")
async def root(request: Request):
    """Redirect to student welcome page."""
    return RedirectResponse(url="/student/welcome")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)