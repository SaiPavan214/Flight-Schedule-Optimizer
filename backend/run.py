#!/usr/bin/env python3
"""
Main entry point for the Airport Operations API
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print("🚀 Starting Airport Operations API...")
    print(f"📍 Server will run on http://{settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🔧 Debug mode: {settings.debug}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
