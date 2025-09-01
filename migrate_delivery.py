#!/usr/bin/env python3
"""
Migration script to add delivery features to existing database
"""

import sqlite3
import os
from datetime import datetime, timedelta

def migrate_delivery_features():
    """Add delivery features to existing database"""
    
    print("🚚 Migrating database for delivery features...")
    
    db_path = "logistics_agent.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Please run migrate_to_database.py first")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create couriers table
        print("📊 Creating couriers table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS couriers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                courier_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                service_type TEXT,
                api_endpoint TEXT,
                api_key TEXT,
                avg_delivery_days INTEGER DEFAULT 3,
                coverage_area TEXT,
                cost_per_kg REAL DEFAULT 5.0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create shipments table
        print("📊 Creating shipments table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shipments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shipment_id TEXT UNIQUE NOT NULL,
                order_id INTEGER NOT NULL,
                courier_id TEXT NOT NULL,
                tracking_number TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'created',
                origin_address TEXT,
                destination_address TEXT,
                estimated_delivery TIMESTAMP,
                actual_delivery TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                picked_up_at TIMESTAMP,
                delivered_at TIMESTAMP,
                notes TEXT
            )
        """)
        
        # Create delivery_events table
        print("📊 Creating delivery_events table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS delivery_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shipment_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_description TEXT,
                location TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                courier_notes TEXT
            )
        """)
        
        # Insert sample couriers if they don't exist
        cursor.execute("SELECT COUNT(*) FROM couriers")
        courier_count = cursor.fetchone()[0]
        
        if courier_count == 0:
            print("📊 Adding sample couriers...")
            couriers = [
                ('COURIER_001', 'FastShip Express', 'express', 'http://localhost:9001/api/courier', 2, 'National', 8.50),
                ('COURIER_002', 'Standard Delivery Co.', 'standard', 'http://localhost:9002/api/courier', 5, 'Regional', 4.25),
                ('COURIER_003', 'Overnight Rush', 'overnight', 'http://localhost:9003/api/courier', 1, 'Metro', 15.00)
            ]
            
            cursor.executemany("""
                INSERT INTO couriers (courier_id, name, service_type, api_endpoint, avg_delivery_days, coverage_area, cost_per_kg)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, couriers)
            
            print(f"✅ Added {len(couriers)} couriers")
        
        # Insert sample shipments for existing orders
        cursor.execute("SELECT COUNT(*) FROM shipments")
        shipment_count = cursor.fetchone()[0]
        
        if shipment_count == 0:
            print("📊 Adding sample shipments...")
            
            # Get existing orders
            cursor.execute("SELECT order_id FROM orders LIMIT 3")
            orders = cursor.fetchall()
            
            if orders:
                shipments = []
                for i, (order_id,) in enumerate(orders):
                    courier_ids = ['COURIER_001', 'COURIER_002', 'COURIER_003']
                    courier_id = courier_ids[i % len(courier_ids)]
                    
                    shipment_id = f'SHIP_{order_id:03d}'
                    tracking_number = f'{courier_id[:2]}{100000000 + i}'
                    
                    # Vary shipment statuses for demo
                    statuses = ['in_transit', 'delivered', 'out_for_delivery']
                    status = statuses[i % len(statuses)]
                    
                    estimated_delivery = datetime.now() + timedelta(days=2)
                    actual_delivery = datetime.now() - timedelta(days=1) if status == 'delivered' else None
                    
                    shipments.append((
                        shipment_id,
                        order_id,
                        courier_id,
                        tracking_number,
                        status,
                        'Warehouse A, 123 Main St',
                        f'Customer Address {i+1}',
                        estimated_delivery.isoformat(),
                        actual_delivery.isoformat() if actual_delivery else None
                    ))
                
                cursor.executemany("""
                    INSERT INTO shipments (shipment_id, order_id, courier_id, tracking_number, status, 
                                         origin_address, destination_address, estimated_delivery, actual_delivery)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, shipments)
                
                print(f"✅ Added {len(shipments)} sample shipments")
                
                # Add some delivery events
                print("📊 Adding sample delivery events...")
                events = []
                for i, (order_id,) in enumerate(orders):
                    shipment_id = f'SHIP_{order_id:03d}'
                    
                    # Add creation event
                    events.append((
                        shipment_id,
                        'status_update',
                        'Shipment created and ready for pickup',
                        'Processing Center',
                        (datetime.now() - timedelta(hours=24)).isoformat()
                    ))
                    
                    # Add pickup event
                    events.append((
                        shipment_id,
                        'status_update',
                        'Package picked up from sender',
                        'Origin Facility',
                        (datetime.now() - timedelta(hours=20)).isoformat()
                    ))
                    
                    # Add transit event
                    events.append((
                        shipment_id,
                        'location_update',
                        'Package in transit to destination',
                        'Distribution Center',
                        (datetime.now() - timedelta(hours=12)).isoformat()
                    ))
                
                cursor.executemany("""
                    INSERT INTO delivery_events (shipment_id, event_type, event_description, location, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, events)
                
                print(f"✅ Added {len(events)} delivery events")
        
        # Update some orders to 'Processing' status to trigger delivery agent
        print("📊 Setting up orders for delivery processing...")
        cursor.execute("""
            UPDATE orders 
            SET status = 'Processing' 
            WHERE order_id IN (103, 104, 105)
        """)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Delivery migration completed successfully!")
        
        # Show summary
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM couriers")
        courier_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM shipments")
        shipment_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM delivery_events")
        event_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Processing'")
        processing_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT shipment_id, status, tracking_number FROM shipments")
        shipments = cursor.fetchall()
        
        conn.close()
        
        print(f"\n📊 Delivery Database Summary:")
        print(f"   - Couriers: {courier_count}")
        print(f"   - Shipments: {shipment_count}")
        print(f"   - Delivery Events: {event_count}")
        print(f"   - Orders Ready for Shipment: {processing_orders}")
        
        if shipments:
            print(f"   - Sample Shipments:")
            for shipment_id, status, tracking in shipments:
                print(f"     • {shipment_id}: {status} (Tracking: {tracking})")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚚 AI Agent Delivery Migration")
    print("Adding delivery features to existing database")
    print()
    
    success = migrate_delivery_features()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("🚀 Ready to run delivery agent!")
        print("   - Run: python3 delivery_agent.py")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
