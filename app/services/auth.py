from sqlalchemy.orm import Session
from ..models import Admin
from ..schemas import AdminCreate, AdminLogin
from ..utils.security import verify_password, get_password_hash, create_access_token
from typing import Optional

def authenticate_admin(db: Session, username: str, password: str) -> Optional[Admin]:
    """Authenticate admin user with username and password."""
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin

def create_admin(db: Session, admin: AdminCreate) -> Admin:
    """Create a new admin user."""
    hashed_password = get_password_hash(admin.password)
    db_admin = Admin(
        username=admin.username,
        password_hash=hashed_password
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def get_admin_by_username(db: Session, username: str) -> Optional[Admin]:
    """Get admin by username."""
    return db.query(Admin).filter(Admin.username == username).first()

def login_admin(db: Session, login_data: AdminLogin) -> Optional[str]:
    """Login admin and return access token."""
    admin = authenticate_admin(db, login_data.username, login_data.password)
    if not admin:
        return None
    
    access_token = create_access_token(data={"sub": admin.username})
    return access_token