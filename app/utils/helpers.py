import uuid
import os
from typing import Optional
from fastapi import UploadFile

def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())

def save_upload_file(file: UploadFile, upload_dir: str = "app/static/uploads/images") -> Optional[str]:
    """Save an uploaded file and return the file path."""
    if not file:
        return None
    
    # Create directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    # Return relative path for database storage
    return f"static/uploads/images/{filename}"

def delete_file(file_path: str) -> bool:
    """Delete a file if it exists."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False

def validate_image_file(file: UploadFile) -> bool:
    """Validate that the uploaded file is an image."""
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    if not file.filename:
        return False
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    return file_extension in allowed_extensions

def format_datetime(dt) -> str:
    """Format datetime for display."""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"