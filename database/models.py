#!/usr/bin/env python3
"""
Database models for AI Agent Logistics System
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Order(Base):
    """Order model"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, unique=True, nullable=False, index=True)
    status = Column(String(50), nullable=False)
    customer_id = Column(String(100))
    product_id = Column(String(50))
    quantity = Column(Integer)
    order_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Order(order_id={self.order_id}, status='{self.status}')>"

class Return(Base):
    """Return model"""
    __tablename__ = 'returns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), nullable=False, index=True)
    return_quantity = Column(Integer, nullable=False)
    reason = Column(String(200))
    return_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Return(product_id='{self.product_id}', quantity={self.return_quantity})>"

class RestockRequest(Base):
    """Restock request model"""
    __tablename__ = 'restock_requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), nullable=False, index=True)
    restock_quantity = Column(Integer, nullable=False)
    status = Column(String(50), default='pending')  # pending, approved, completed
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<RestockRequest(product_id='{self.product_id}', quantity={self.restock_quantity}, status='{self.status}')>"

class AgentLog(Base):
    """Agent action log model"""
    __tablename__ = 'agent_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    action = Column(String(100), nullable=False)
    product_id = Column(String(50))
    quantity = Column(Integer)
    confidence = Column(Float)
    human_review = Column(Boolean, default=False)
    details = Column(Text)
    
    def __repr__(self):
        return f"<AgentLog(action='{self.action}', product_id='{self.product_id}')>"

class HumanReview(Base):
    """Human review model"""
    __tablename__ = 'human_reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(String(100), unique=True, nullable=False, index=True)
    action_type = Column(String(50), nullable=False)
    data = Column(Text)  # JSON data
    decision_description = Column(Text)
    confidence = Column(Float)
    status = Column(String(20), default='pending')  # pending, approved, rejected
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    reviewer_notes = Column(Text)
    
    def __repr__(self):
        return f"<HumanReview(review_id='{self.review_id}', status='{self.status}')>"

class Inventory(Base):
    """Inventory model"""
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), unique=True, nullable=False, index=True)
    current_stock = Column(Integer, default=0)
    reserved_stock = Column(Integer, default=0)  # Stock reserved for orders
    reorder_point = Column(Integer, default=10)
    max_stock = Column(Integer, default=100)
    supplier_id = Column(String(50), default='SUPPLIER_001')
    unit_cost = Column(Float, default=10.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def available_stock(self):
        return self.current_stock - self.reserved_stock

    @property
    def needs_reorder(self):
        return self.current_stock <= self.reorder_point

    def __repr__(self):
        return f"<Inventory(product_id='{self.product_id}', stock={self.current_stock})>"

class PurchaseOrder(Base):
    """Purchase Order model"""
    __tablename__ = 'purchase_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    po_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_id = Column(String(50), nullable=False)
    product_id = Column(String(50), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    status = Column(String(20), default='pending')  # pending, sent, confirmed, delivered, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    confirmed_at = Column(DateTime)
    expected_delivery = Column(DateTime)
    delivered_at = Column(DateTime)
    notes = Column(Text)

    def __repr__(self):
        return f"<PurchaseOrder(po_number='{self.po_number}', product='{self.product_id}', status='{self.status}')>"

class Supplier(Base):
    """Supplier model"""
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    contact_email = Column(String(200))
    contact_phone = Column(String(50))
    api_endpoint = Column(String(500))  # For API integration
    api_key = Column(String(200))
    lead_time_days = Column(Integer, default=7)
    minimum_order = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Supplier(supplier_id='{self.supplier_id}', name='{self.name}')>"

class Shipment(Base):
    """Shipment model for delivery tracking"""
    __tablename__ = 'shipments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    courier_id = Column(String(50), nullable=False)
    tracking_number = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), default='created')  # created, picked_up, in_transit, out_for_delivery, delivered, failed
    origin_address = Column(Text)
    destination_address = Column(Text)
    estimated_delivery = Column(DateTime)
    actual_delivery = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    picked_up_at = Column(DateTime)
    delivered_at = Column(DateTime)
    notes = Column(Text)

    def __repr__(self):
        return f"<Shipment(shipment_id='{self.shipment_id}', status='{self.status}')>"

class Courier(Base):
    """Courier/delivery service model"""
    __tablename__ = 'couriers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    courier_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    service_type = Column(String(100))  # standard, express, overnight
    api_endpoint = Column(String(500))
    api_key = Column(String(200))
    avg_delivery_days = Column(Integer, default=3)
    coverage_area = Column(String(200))
    cost_per_kg = Column(Float, default=5.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Courier(courier_id='{self.courier_id}', name='{self.name}')>"

class DeliveryEvent(Base):
    """Delivery tracking events"""
    __tablename__ = 'delivery_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(String(50), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # status_update, location_update, delivery_attempt
    event_description = Column(Text)
    location = Column(String(200))
    timestamp = Column(DateTime, default=datetime.utcnow)
    courier_notes = Column(Text)

    def __repr__(self):
        return f"<DeliveryEvent(shipment_id='{self.shipment_id}', event='{self.event_type}')>"

class Alert(Base):
    """System alerts and notifications"""
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(50), unique=True, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # stockout, delay, error, threshold
    severity = Column(String(20), default='medium')  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    entity_type = Column(String(50))  # order, product, shipment, supplier
    entity_id = Column(String(50))
    status = Column(String(20), default='active')  # active, acknowledged, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    acknowledged_by = Column(String(100))
    resolved_by = Column(String(100))

    def __repr__(self):
        return f"<Alert(alert_id='{self.alert_id}', type='{self.alert_type}', severity='{self.severity}')>"

class KPIMetric(Base):
    """KPI metrics tracking"""
    __tablename__ = 'kpi_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))  # percentage, count, currency, time
    category = Column(String(50))  # performance, efficiency, quality, financial
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    period_type = Column(String(20), default='daily')  # hourly, daily, weekly, monthly

    def __repr__(self):
        return f"<KPIMetric(name='{self.metric_name}', value={self.metric_value})>"

class NotificationLog(Base):
    """Notification delivery log"""
    __tablename__ = 'notification_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    notification_id = Column(String(50), unique=True, nullable=False)
    notification_type = Column(String(50), nullable=False)  # email, sms, push, console
    recipient = Column(String(200))
    subject = Column(String(200))
    message = Column(Text)
    status = Column(String(20), default='pending')  # pending, sent, delivered, failed
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    error_message = Column(Text)

    def __repr__(self):
        return f"<NotificationLog(id='{self.notification_id}', type='{self.notification_type}', status='{self.status}')>"

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///logistics_agent.db')

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with sample data"""
    create_tables()
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Order).first():
            print("📊 Database already has data, skipping initialization")
            return
        
        # Add sample orders
        sample_orders = [
            Order(order_id=101, status='Shipped', customer_id='CUST001', product_id='A101', quantity=2),
            Order(order_id=102, status='Delivered', customer_id='CUST002', product_id='B202', quantity=1),
            Order(order_id=103, status='Processing', customer_id='CUST003', product_id='C303', quantity=3),
            Order(order_id=104, status='Cancelled', customer_id='CUST004', product_id='D404', quantity=1),
            Order(order_id=105, status='In Transit', customer_id='CUST005', product_id='E505', quantity=2),
        ]
        
        # Add sample returns
        sample_returns = [
            Return(product_id='A101', return_quantity=6, reason='Defective'),
            Return(product_id='B202', return_quantity=3, reason='Wrong size'),
            Return(product_id='C303', return_quantity=25, reason='Bulk return'),
            Return(product_id='D404', return_quantity=2, reason='Not needed'),
            Return(product_id='E505', return_quantity=12, reason='Damaged'),
        ]
        
        # Add sample suppliers
        sample_suppliers = [
            Supplier(
                supplier_id='SUPPLIER_001',
                name='TechParts Supply Co.',
                contact_email='orders@techparts.com',
                contact_phone='+1-555-0101',
                api_endpoint='http://localhost:8001/api/supplier',
                lead_time_days=5,
                minimum_order=10
            ),
            Supplier(
                supplier_id='SUPPLIER_002',
                name='Global Components Ltd.',
                contact_email='procurement@globalcomp.com',
                contact_phone='+1-555-0102',
                api_endpoint='http://localhost:8002/api/supplier',
                lead_time_days=7,
                minimum_order=5
            ),
            Supplier(
                supplier_id='SUPPLIER_003',
                name='FastTrack Logistics',
                contact_email='orders@fasttrack.com',
                contact_phone='+1-555-0103',
                api_endpoint='http://localhost:8003/api/supplier',
                lead_time_days=3,
                minimum_order=20
            )
        ]

        # Add sample couriers
        sample_couriers = [
            Courier(
                courier_id='COURIER_001',
                name='FastShip Express',
                service_type='express',
                api_endpoint='http://localhost:9001/api/courier',
                avg_delivery_days=2,
                coverage_area='National',
                cost_per_kg=8.50
            ),
            Courier(
                courier_id='COURIER_002',
                name='Standard Delivery Co.',
                service_type='standard',
                api_endpoint='http://localhost:9002/api/courier',
                avg_delivery_days=5,
                coverage_area='Regional',
                cost_per_kg=4.25
            ),
            Courier(
                courier_id='COURIER_003',
                name='Overnight Rush',
                service_type='overnight',
                api_endpoint='http://localhost:9003/api/courier',
                avg_delivery_days=1,
                coverage_area='Metro',
                cost_per_kg=15.00
            )
        ]

        # Add sample inventory with supplier assignments
        sample_inventory = [
            Inventory(product_id='A101', current_stock=8, reorder_point=10, supplier_id='SUPPLIER_001', unit_cost=15.50),  # Below reorder point
            Inventory(product_id='B202', current_stock=3, reorder_point=5, supplier_id='SUPPLIER_002', unit_cost=22.00),   # Below reorder point
            Inventory(product_id='C303', current_stock=100, reorder_point=20, supplier_id='SUPPLIER_001', unit_cost=8.75),
            Inventory(product_id='D404', current_stock=15, reorder_point=8, supplier_id='SUPPLIER_003', unit_cost=45.00),
            Inventory(product_id='E505', current_stock=2, reorder_point=15, supplier_id='SUPPLIER_002', unit_cost=12.25),  # Below reorder point
        ]
        
        # Add sample shipments for existing orders
        sample_shipments = [
            Shipment(
                shipment_id='SHIP_001',
                order_id=101,
                courier_id='COURIER_001',
                tracking_number='FS123456789',
                status='in_transit',
                origin_address='Warehouse A, 123 Main St',
                destination_address='Customer Address 1',
                estimated_delivery=datetime.utcnow() + timedelta(days=2)
            ),
            Shipment(
                shipment_id='SHIP_002',
                order_id=102,
                courier_id='COURIER_002',
                tracking_number='SD987654321',
                status='delivered',
                origin_address='Warehouse A, 123 Main St',
                destination_address='Customer Address 2',
                estimated_delivery=datetime.utcnow() - timedelta(days=1),
                actual_delivery=datetime.utcnow() - timedelta(days=1)
            ),
            Shipment(
                shipment_id='SHIP_003',
                order_id=103,
                courier_id='COURIER_003',
                tracking_number='OR555666777',
                status='out_for_delivery',
                origin_address='Warehouse A, 123 Main St',
                destination_address='Customer Address 3',
                estimated_delivery=datetime.utcnow()
            )
        ]

        # Add to database
        db.add_all(sample_orders)
        db.add_all(sample_returns)
        db.add_all(sample_suppliers)
        db.add_all(sample_couriers)
        db.add_all(sample_inventory)
        db.add_all(sample_shipments)
        db.commit()

        print("✅ Database initialized with sample data")
        print(f"   - {len(sample_orders)} orders")
        print(f"   - {len(sample_returns)} returns")
        print(f"   - {len(sample_suppliers)} suppliers")
        print(f"   - {len(sample_couriers)} couriers")
        print(f"   - {len(sample_inventory)} inventory items")
        print(f"   - {len(sample_shipments)} shipments")
        print(f"   - {sum(1 for inv in sample_inventory if inv.needs_reorder)} items need reordering")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
