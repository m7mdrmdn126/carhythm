#!/usr/bin/env python3
"""
Script to add a new admin user to the database
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.models import Admin, get_db
from app.utils.security import get_password_hash

def add_admin_user(username: str, password: str):
    """Add a new admin user to the database."""
    db = next(get_db())
    
    try:
        # Check if admin already exists
        existing_admin = db.query(Admin).filter(Admin.username == username).first()
        
        if existing_admin:
            print(f"❌ Admin user '{username}' already exists!")
            return False
        
        # Create new admin
        admin = Admin(
            username=username,
            password_hash=get_password_hash(password)
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"✅ Successfully created admin user: {username}")
        print(f"📝 Username: {username}")
        print(f"🔐 Password: {password}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Adding Admin User to Database")
    print("=" * 50)
    
    # Add the specified admin user
    add_admin_user("MO", "MOMO126")
