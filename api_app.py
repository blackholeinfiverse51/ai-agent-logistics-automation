from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from database.service import DatabaseService
from database.models import init_database
import agent_db
from datetime import datetime
from typing import List
from auth_system import (
    auth_system, get_current_user, require_permission, require_role,
    User, UserLogin, UserCreate, Token
)

app = FastAPI(
    title="AI Agent Logistics API",
    description="Secure Database-backed API for AI Agent Logistics Automation",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware with security considerations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()
    print("✅ Database initialized")
    print("🔒 Authentication system ready")

@app.get("/")
def read_root():
    return {
        "message": "AI Agent Logistics API",
        "version": "3.0.0",
        "status": "operational",
        "security": "JWT Authentication Enabled",
        "features": [
            "Order management",
            "Inventory tracking",
            "Returns processing",
            "Procurement automation",
            "Delivery tracking",
            "Dashboard analytics",
            "User authentication",
            "Role-based access control"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    try:
        with DatabaseService() as db_service:
            # Test database connection
            db_service.get_orders(limit=1)
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# === AUTHENTICATION ENDPOINTS ===

@app.post("/auth/login", response_model=Token)
def login(login_data: UserLogin):
    """User login"""
    return auth_system.login(login_data)

@app.post("/auth/refresh", response_model=Token)
def refresh_token(refresh_token: str):
    """Refresh access token"""
    return auth_system.refresh_access_token(refresh_token)

@app.post("/auth/logout")
def logout(refresh_token: str):
    """User logout"""
    success = auth_system.logout(refresh_token)
    return {"message": "Logged out successfully" if success else "Logout failed"}

@app.post("/auth/register", response_model=User)
def register(user_data: UserCreate, current_user: User = Depends(require_role("admin"))):
    """Register new user (admin only)"""
    return auth_system.create_user(user_data)

@app.get("/auth/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/auth/users", response_model=List[User])
def list_users(current_user: User = Depends(require_role("admin"))):
    """List all users (admin only)"""
    return auth_system.list_users()

@app.get("/orders")
def get_orders(limit: int = 100, current_user: User = Depends(require_permission("read:orders"))):
    """Get orders from database (requires read:orders permission)"""
    try:
        with DatabaseService() as db_service:
            orders = db_service.get_orders(limit=limit)
        return {"orders": orders, "count": len(orders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    """Get specific order by ID"""
    try:
        with DatabaseService() as db_service:
            order = db_service.get_order_by_id(order_id)
        if order:
            return order
        else:
            raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/returns")
def get_returns(processed: bool = None):
    """Get returns from database"""
    try:
        with DatabaseService() as db_service:
            returns = db_service.get_returns(processed=processed)
        return {"returns": returns, "count": len(returns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/restock-requests")
def get_restock_requests(status: str = None):
    """Get restock requests"""
    try:
        with DatabaseService() as db_service:
            requests = db_service.get_restock_requests(status=status)
        return {"restock_requests": requests, "count": len(requests)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inventory")
def get_inventory():
    """Get inventory status"""
    try:
        with DatabaseService() as db_service:
            inventory = db_service.get_inventory()
        return {"inventory": inventory, "count": len(inventory)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inventory/low-stock")
def get_low_stock():
    """Get low stock items"""
    try:
        with DatabaseService() as db_service:
            low_stock = db_service.get_low_stock_items()
        return {"low_stock_items": low_stock, "count": len(low_stock)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/status")
def get_agent_status():
    """Get agent status and metrics"""
    try:
        status = agent_db.get_agent_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/run")
def run_agent():
    """Trigger agent execution"""
    try:
        success = agent_db.run_agent()
        return {"success": success, "message": "Agent execution completed" if success else "Agent execution failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reviews/pending")
def get_pending_reviews():
    """Get pending human reviews"""
    try:
        with DatabaseService() as db_service:
            reviews = db_service.get_pending_reviews()
        return {"pending_reviews": reviews, "count": len(reviews)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
def get_agent_logs(limit: int = 100):
    """Get agent logs"""
    try:
        with DatabaseService() as db_service:
            logs = db_service.get_agent_logs(limit=limit)
        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/performance")
def get_performance_metrics(days: int = 7):
    """Get performance analytics"""
    try:
        with DatabaseService() as db_service:
            metrics = db_service.get_performance_metrics(days=days)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoints for backward compatibility
@app.get("/get_orders")
def get_orders_legacy():
    """Legacy endpoint - redirects to /orders"""
    return get_orders()

@app.get("/get_returns")
def get_returns_legacy():
    """Legacy endpoint - redirects to /returns"""
    return get_returns()

@app.get("/procurement/purchase-orders")
def get_purchase_orders(status: str = None):
    """Get purchase orders"""
    try:
        with DatabaseService() as db_service:
            orders = db_service.get_purchase_orders(status=status)
        return {"purchase_orders": orders, "count": len(orders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/procurement/suppliers")
def get_suppliers():
    """Get suppliers"""
    try:
        with DatabaseService() as db_service:
            suppliers = db_service.get_suppliers()
        return {"suppliers": suppliers, "count": len(suppliers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/procurement/run")
def run_procurement():
    """Trigger procurement agent"""
    try:
        from procurement_agent import run_procurement_agent
        results = run_procurement_agent()
        return {
            "success": True,
            "results": results,
            "message": f"Procurement cycle completed: {results['purchase_orders_created']} POs created, {results['items_submitted_for_review']} items for review"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/delivery/shipments")
def get_shipments(status: str = None):
    """Get shipments"""
    try:
        with DatabaseService() as db_service:
            shipments = db_service.get_shipments(status=status)
        return {"shipments": shipments, "count": len(shipments)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/delivery/track/{tracking_number}")
def track_shipment(tracking_number: str):
    """Track shipment by tracking number"""
    try:
        with DatabaseService() as db_service:
            shipment = db_service.get_shipment_by_tracking(tracking_number)
        if shipment:
            return shipment
        else:
            raise HTTPException(status_code=404, detail="Tracking number not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/delivery/order/{order_id}")
def get_shipment_by_order(order_id: int):
    """Get shipment by order ID"""
    try:
        with DatabaseService() as db_service:
            shipment = db_service.get_shipment_by_order(order_id)
        if shipment:
            return shipment
        else:
            raise HTTPException(status_code=404, detail="No shipment found for this order")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/delivery/couriers")
def get_couriers():
    """Get couriers"""
    try:
        with DatabaseService() as db_service:
            couriers = db_service.get_couriers()
        return {"couriers": couriers, "count": len(couriers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delivery/run")
def run_delivery():
    """Trigger delivery agent"""
    try:
        from delivery_agent import run_delivery_agent
        results = run_delivery_agent()
        return {
            "success": True,
            "results": results,
            "message": f"Delivery cycle completed: {results['shipments_created']} shipments created, {results['shipments_updated']} updated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/kpis")
def get_dashboard_kpis():
    """Get dashboard KPIs"""
    try:
        with DatabaseService() as db_service:
            orders = db_service.get_orders()
            shipments = db_service.get_shipments()
            inventory = db_service.get_inventory()
            low_stock = db_service.get_low_stock_items()
            purchase_orders = db_service.get_purchase_orders()
            pending_reviews = db_service.get_pending_reviews()
            performance = db_service.get_performance_metrics(days=7)

            # Calculate KPIs
            total_orders = len(orders)
            active_shipments = len([s for s in shipments if s['status'] not in ['delivered', 'cancelled']])
            delivered_shipments = len([s for s in shipments if s['status'] == 'delivered'])
            delivery_rate = (delivered_shipments / len(shipments) * 100) if shipments else 0

            low_stock_count = len(low_stock)
            stock_health = ((len(inventory) - low_stock_count) / len(inventory) * 100) if inventory else 100

            pending_pos = len([po for po in purchase_orders if po['status'] == 'pending'])
            automation_rate = performance.get('automation_rate', 0)

            kpis = {
                'total_orders': total_orders,
                'active_shipments': active_shipments,
                'delivery_rate': round(delivery_rate, 1),
                'stock_health': round(stock_health, 1),
                'low_stock_count': low_stock_count,
                'pending_pos': pending_pos,
                'automation_rate': round(automation_rate, 1),
                'pending_reviews': len(pending_reviews)
            }

        return {"kpis": kpis, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/alerts")
def get_dashboard_alerts():
    """Get system alerts"""
    try:
        from notification_system import NotificationSystem
        notif_system = NotificationSystem()

        # Get all types of alerts
        stock_alerts = notif_system.check_stock_alerts()
        delivery_alerts = notif_system.check_delivery_alerts()
        system_alerts = notif_system.check_system_alerts()

        all_alerts = stock_alerts + delivery_alerts + system_alerts

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_alerts.sort(key=lambda x: severity_order.get(x['severity'], 4))

        return {"alerts": all_alerts, "count": len(all_alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dashboard/notifications/run")
def run_notification_system():
    """Trigger notification system"""
    try:
        from notification_system import run_notification_system
        results = run_notification_system()
        return {
            "success": True,
            "results": results,
            "message": f"Notification cycle completed: {results['alerts_created']} alerts, {results['notifications_sent']} notifications"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/activity")
def get_recent_activity():
    """Get recent system activity"""
    try:
        with DatabaseService() as db_service:
            logs = db_service.get_agent_logs(limit=20)

            # Format logs for dashboard
            formatted_logs = []
            for log in logs:
                formatted_logs.append({
                    'timestamp': log['timestamp'],
                    'action': log['action'],
                    'product_id': log['ProductID'],
                    'quantity': log['quantity'],
                    'confidence': log['confidence'],
                    'human_review': log['human_review'],
                    'details': log['details'][:100] + '...' if log['details'] and len(log['details']) > 100 else log['details']
                })

        return {"activity": formatted_logs, "count": len(formatted_logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Agent Logistics API Server...")
    print("📊 Dashboard: http://localhost:8501")
    print("🌐 API Docs: http://localhost:8000/docs")
    print("🔒 Authentication: JWT enabled")
    uvicorn.run(app, host="0.0.0.0", port=8000)
