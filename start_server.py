#!/usr/bin/env python3
"""
Simple server startup script for AI Agent Logistics
"""

import uvicorn
from api_app import app

if __name__ == "__main__":
    print("🚀 Starting AI Agent Logistics API Server...")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔒 Authentication: JWT enabled")
    print("👤 Default users: admin/admin123, manager/manager123, operator/operator123, viewer/viewer123")
    print("=" * 60)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
