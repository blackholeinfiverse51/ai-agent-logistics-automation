#!/usr/bin/env python3
"""
Simple test server for AI Agent Logistics
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.service import DatabaseService
from database.models import init_database
from datetime import datetime
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="AI Agent Logistics API",
    description="Secure Database-backed API for AI Agent Logistics Automation",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()
    print("✅ Database initialized")

@app.get("/")
def read_root():
    return {
        "message": "AI Agent Logistics API",
        "version": "3.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Order management",
            "Inventory tracking", 
            "Returns processing",
            "Procurement automation",
            "Delivery tracking",
            "Dashboard analytics"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    try:
        with DatabaseService() as db_service:
            # Test database connection
            orders = db_service.get_orders(limit=1)
        return {
            "status": "healthy", 
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/orders")
def get_orders(limit: int = 100):
    """Get orders from database"""
    try:
        with DatabaseService() as db_service:
            orders = db_service.get_orders(limit=limit)
        return {"orders": orders, "count": len(orders)}
    except Exception as e:
        return {"error": str(e)}

@app.get("/inventory")
def get_inventory():
    """Get inventory from database"""
    try:
        with DatabaseService() as db_service:
            inventory = db_service.get_inventory()
        return {"inventory": inventory, "count": len(inventory)}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting AI Agent Logistics API Server...")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
