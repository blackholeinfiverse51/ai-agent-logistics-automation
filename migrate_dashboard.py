#!/usr/bin/env python3
"""
Migration script to add dashboard and notification features to existing database
"""

import sqlite3
import os
from datetime import datetime, timedelta
import json

def migrate_dashboard_features():
    """Add dashboard and notification features to existing database"""
    
    print("📊 Migrating database for dashboard features...")
    
    db_path = "logistics_agent.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Please run migrate_to_database.py first")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create alerts table
        print("📊 Creating alerts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT DEFAULT 'medium',
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                entity_type TEXT,
                entity_id TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged_at TIMESTAMP,
                resolved_at TIMESTAMP,
                acknowledged_by TEXT,
                resolved_by TEXT
            )
        """)
        
        # Create KPI metrics table
        print("📊 Creating kpi_metrics table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kpi_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                category TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                period_type TEXT DEFAULT 'daily'
            )
        """)
        
        # Create notification logs table
        print("📊 Creating notification_logs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notification_id TEXT UNIQUE NOT NULL,
                notification_type TEXT NOT NULL,
                recipient TEXT,
                subject TEXT,
                message TEXT,
                status TEXT DEFAULT 'pending',
                sent_at TIMESTAMP,
                delivered_at TIMESTAMP,
                error_message TEXT
            )
        """)
        
        # Insert sample alerts
        cursor.execute("SELECT COUNT(*) FROM alerts")
        alert_count = cursor.fetchone()[0]
        
        if alert_count == 0:
            print("📊 Adding sample alerts...")
            
            sample_alerts = [
                (
                    'ALERT_20250823_001',
                    'low_stock',
                    'high',
                    'LOW STOCK: A101',
                    'Product A101 stock is critically low (8 units, reorder at 10).',
                    'product',
                    'A101',
                    'active',
                    datetime.now().isoformat()
                ),
                (
                    'ALERT_20250823_002',
                    'stockout',
                    'critical',
                    'STOCKOUT: B202',
                    'Product B202 is completely out of stock. Immediate action required.',
                    'product',
                    'B202',
                    'active',
                    datetime.now().isoformat()
                ),
                (
                    'ALERT_20250823_003',
                    'review_backlog',
                    'medium',
                    'HIGH REVIEW BACKLOG',
                    '6 items are pending human review. Consider reviewing to maintain automation efficiency.',
                    'system',
                    'review_queue',
                    'active',
                    datetime.now().isoformat()
                )
            ]
            
            cursor.executemany("""
                INSERT INTO alerts (alert_id, alert_type, severity, title, message, entity_type, entity_id, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_alerts)
            
            print(f"✅ Added {len(sample_alerts)} sample alerts")
        
        # Insert sample KPI metrics
        cursor.execute("SELECT COUNT(*) FROM kpi_metrics")
        kpi_count = cursor.fetchone()[0]
        
        if kpi_count == 0:
            print("📊 Adding sample KPI metrics...")
            
            base_time = datetime.now()
            sample_kpis = []
            
            # Generate KPIs for the last 7 days
            for i in range(7):
                day_time = base_time - timedelta(days=i)
                
                # Daily metrics with some variation
                sample_kpis.extend([
                    ('automation_rate', 75.5 + (i * 2), 'percentage', 'performance', day_time.isoformat(), 'daily'),
                    ('delivery_rate', 92.3 + (i * 0.5), 'percentage', 'efficiency', day_time.isoformat(), 'daily'),
                    ('stock_health', 88.7 - (i * 1.2), 'percentage', 'quality', day_time.isoformat(), 'daily'),
                    ('total_orders', 45 + (i * 3), 'count', 'performance', day_time.isoformat(), 'daily'),
                    ('active_shipments', 12 + i, 'count', 'performance', day_time.isoformat(), 'daily')
                ])
            
            cursor.executemany("""
                INSERT INTO kpi_metrics (metric_name, metric_value, metric_unit, category, timestamp, period_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, sample_kpis)
            
            print(f"✅ Added {len(sample_kpis)} KPI metrics")
        
        # Insert sample notification logs
        cursor.execute("SELECT COUNT(*) FROM notification_logs")
        notif_count = cursor.fetchone()[0]
        
        if notif_count == 0:
            print("📊 Adding sample notification logs...")
            
            sample_notifications = [
                (
                    'NOTIF_20250823_001',
                    'email',
                    'operations@company.com',
                    'CRITICAL: Product B202 Out of Stock',
                    'Product B202 is completely out of stock. Immediate restocking required.',
                    'sent',
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ),
                (
                    'NOTIF_20250823_002',
                    'console',
                    'system_admin',
                    'LOW STOCK: Product A101',
                    'Product A101 stock is critically low (8 units, reorder at 10).',
                    'sent',
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ),
                (
                    'NOTIF_20250823_003',
                    'sms',
                    '+1-555-0199',
                    'Delivery Delay Alert',
                    'Shipment CO100000000 has been delayed. Expected delivery updated.',
                    'sent',
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                )
            ]
            
            cursor.executemany("""
                INSERT INTO notification_logs (notification_id, notification_type, recipient, subject, message, status, sent_at, delivered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_notifications)
            
            print(f"✅ Added {len(sample_notifications)} notification logs")
        
        # Create indexes for better performance
        print("📊 Creating performance indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_alerts_type_severity ON alerts(alert_type, severity)",
            "CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)",
            "CREATE INDEX IF NOT EXISTS idx_kpi_metrics_name_time ON kpi_metrics(metric_name, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_notification_logs_type ON notification_logs(notification_type)",
            "CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp ON agent_logs(timestamp)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Dashboard migration completed successfully!")
        
        # Show summary
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM alerts")
        alert_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM kpi_metrics")
        kpi_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notification_logs")
        notif_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT alert_type, severity, COUNT(*) FROM alerts GROUP BY alert_type, severity")
        alert_breakdown = cursor.fetchall()
        
        conn.close()
        
        print(f"\n📊 Dashboard Database Summary:")
        print(f"   - Alerts: {alert_count}")
        print(f"   - KPI Metrics: {kpi_count}")
        print(f"   - Notification Logs: {notif_count}")
        
        if alert_breakdown:
            print(f"   - Alert Breakdown:")
            for alert_type, severity, count in alert_breakdown:
                print(f"     • {alert_type} ({severity}): {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def setup_demo_scenario():
    """Set up demo scenario with alerts and notifications"""
    print("\n🎬 Setting up demo scenario...")
    
    db_path = "logistics_agent.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create some low stock situations
        cursor.execute('UPDATE inventory SET current_stock = 0 WHERE product_id = "B202"')  # Stockout
        cursor.execute('UPDATE inventory SET current_stock = 3 WHERE product_id = "A101"')  # Low stock
        cursor.execute('UPDATE inventory SET current_stock = 1 WHERE product_id = "E505"')  # Very low stock
        
        # Create some delayed shipments
        old_time = (datetime.now() - timedelta(hours=30)).isoformat()
        cursor.execute('UPDATE shipments SET created_at = ?, status = "created" WHERE shipment_id = "SHIP_001"', (old_time,))
        
        # Create overdue delivery
        overdue_time = (datetime.now() - timedelta(days=2)).isoformat()
        cursor.execute('UPDATE shipments SET estimated_delivery = ? WHERE shipment_id = "SHIP_002"', (overdue_time,))
        
        conn.commit()
        conn.close()
        
        print("✅ Demo scenario set up successfully!")
        print("   - Created stockout situation for B202")
        print("   - Set low stock levels for A101 and E505")
        print("   - Created delayed shipment scenario")
        print("   - Set up overdue delivery situation")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo setup failed: {e}")
        conn.close()
        return False

if __name__ == "__main__":
    print("📊 AI Agent Dashboard Migration")
    print("Adding dashboard and notification features to existing database")
    print()
    
    success = migrate_dashboard_features()
    
    if success:
        setup_demo_scenario()
        print("\n🎉 Migration completed successfully!")
        print("🚀 Ready to run dashboard and notification system!")
        print("   - Run: streamlit run dashboard_app.py")
        print("   - Run: python3 notification_system.py")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
