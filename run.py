#!/usr/bin/env python3
"""
Career DNA Assessment Application
Run this script to start the application server
"""

import uvicorn
import os
import sys

def main():
    """Start the FastAPI application"""
    try:
        print("🧬 Starting Career DNA Assessment Application...")
        print("📊 Initializing database and creating tables...")
        
        # Add the project root to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Run the application
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["app"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Career DNA Assessment...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()