#!/usr/bin/env python3
"""
Migration script to add procurement features to existing database
"""

import sqlite3
import os
from database.models import init_database, create_tables

def migrate_procurement_features():
    """Add procurement features to existing database"""
    
    print("🔄 Migrating database for procurement features...")
    
    db_path = "logistics_agent.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Please run migrate_to_database.py first")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(inventory)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'supplier_id' not in columns:
            print("📊 Adding supplier_id and unit_cost columns to inventory table...")
            cursor.execute("ALTER TABLE inventory ADD COLUMN supplier_id TEXT DEFAULT 'SUPPLIER_001'")
            cursor.execute("ALTER TABLE inventory ADD COLUMN unit_cost REAL DEFAULT 10.0")
            print("✅ Inventory table updated")
        else:
            print("✅ Inventory table already has procurement columns")
        
        # Create new tables if they don't exist
        print("📊 Creating procurement tables...")
        
        # Create suppliers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                contact_email TEXT,
                contact_phone TEXT,
                api_endpoint TEXT,
                api_key TEXT,
                lead_time_days INTEGER DEFAULT 7,
                minimum_order INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create purchase_orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchase_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number TEXT UNIQUE NOT NULL,
                supplier_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_cost REAL NOT NULL,
                total_cost REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP,
                confirmed_at TIMESTAMP,
                expected_delivery TIMESTAMP,
                delivered_at TIMESTAMP,
                notes TEXT
            )
        """)
        
        # Insert sample suppliers if they don't exist
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        supplier_count = cursor.fetchone()[0]
        
        if supplier_count == 0:
            print("📊 Adding sample suppliers...")
            suppliers = [
                ('SUPPLIER_001', 'TechParts Supply Co.', 'orders@techparts.com', '+1-555-0101', 'http://localhost:8001/api/supplier', 5, 10),
                ('SUPPLIER_002', 'Global Components Ltd.', 'procurement@globalcomp.com', '+1-555-0102', 'http://localhost:8002/api/supplier', 7, 5),
                ('SUPPLIER_003', 'FastTrack Logistics', 'orders@fasttrack.com', '+1-555-0103', 'http://localhost:8003/api/supplier', 3, 20)
            ]
            
            cursor.executemany("""
                INSERT INTO suppliers (supplier_id, name, contact_email, contact_phone, api_endpoint, lead_time_days, minimum_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, suppliers)
            
            print(f"✅ Added {len(suppliers)} suppliers")
        
        # Update inventory with supplier assignments and costs
        print("📊 Updating inventory with supplier assignments...")
        inventory_updates = [
            ('A101', 'SUPPLIER_001', 15.50),
            ('B202', 'SUPPLIER_002', 22.00),
            ('C303', 'SUPPLIER_001', 8.75),
            ('D404', 'SUPPLIER_003', 45.00),
            ('E505', 'SUPPLIER_002', 12.25)
        ]
        
        for product_id, supplier_id, unit_cost in inventory_updates:
            cursor.execute("""
                UPDATE inventory 
                SET supplier_id = ?, unit_cost = ?
                WHERE product_id = ?
            """, (supplier_id, unit_cost, product_id))
        
        # Set some items to low stock to trigger procurement
        print("📊 Setting low stock levels to trigger procurement...")
        low_stock_updates = [
            ('A101', 8),   # Below reorder point of 10
            ('B202', 3),   # Below reorder point of 5  
            ('E505', 2)    # Below reorder point of 15
        ]
        
        for product_id, stock_level in low_stock_updates:
            cursor.execute("""
                UPDATE inventory 
                SET current_stock = ?
                WHERE product_id = ?
            """, (stock_level, product_id))
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Procurement migration completed successfully!")
        
        # Show summary
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        supplier_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inventory WHERE current_stock <= reorder_point")
        low_stock_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT product_id, current_stock, reorder_point FROM inventory WHERE current_stock <= reorder_point")
        low_stock_items = cursor.fetchall()
        
        conn.close()
        
        print(f"\n📊 Procurement Database Summary:")
        print(f"   - Suppliers: {supplier_count}")
        print(f"   - Low stock items: {low_stock_count}")
        
        if low_stock_items:
            print(f"   - Items needing reorder:")
            for product_id, current, reorder in low_stock_items:
                print(f"     • {product_id}: {current}/{reorder}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🔄 AI Agent Procurement Migration")
    print("Adding procurement features to existing database")
    print()
    
    success = migrate_procurement_features()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("🚀 Ready to run procurement agent!")
        print("   - Run: python3 procurement_agent.py")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
