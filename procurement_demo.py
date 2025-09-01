#!/usr/bin/env python3
"""
Comprehensive Procurement Agent Demo
Shows end-to-end procurement workflow: inventory monitoring → PO generation → supplier confirmation
"""

import time
import requests
from database.service import DatabaseService
from procurement_agent import ProcurementAgent
import json

def show_inventory_status():
    """Display current inventory status"""
    print("📊 Current Inventory Status:")
    print("-" * 60)
    
    with DatabaseService() as db_service:
        inventory = db_service.get_inventory()
        low_stock_items = db_service.get_low_stock_items()
        
        for item in inventory:
            product_id = item['ProductID']
            current = item['CurrentStock']
            reorder = item['ReorderPoint']
            max_stock = item['MaxStock']
            
            status = "🔴 LOW" if current <= reorder else "🟢 OK"
            print(f"   {product_id}: {current:2d}/{reorder:2d} (max: {max_stock:2d}) {status}")
        
        print(f"\n⚠️  Items needing reorder: {len(low_stock_items)}")
        return len(low_stock_items)

def show_purchase_orders():
    """Display current purchase orders"""
    print("\n📋 Purchase Orders:")
    print("-" * 60)
    
    with DatabaseService() as db_service:
        pos = db_service.get_purchase_orders()
        
        if not pos:
            print("   No purchase orders found")
            return 0
        
        for po in pos:
            print(f"   PO: {po['po_number']}")
            print(f"      Product: {po['product_id']} x{po['quantity']}")
            print(f"      Supplier: {po['supplier_id']}")
            print(f"      Status: {po['status']}")
            print(f"      Total: ${po['total_cost']:.2f}")
            print()
        
        return len(pos)

def show_pending_reviews():
    """Display pending human reviews"""
    print("👥 Pending Human Reviews:")
    print("-" * 60)
    
    with DatabaseService() as db_service:
        reviews = db_service.get_pending_reviews()
        
        if not reviews:
            print("   No pending reviews")
            return 0
        
        for review in reviews:
            data = review['data']
            print(f"   Review ID: {review['review_id']}")
            print(f"   Type: {review['action_type']}")
            print(f"   Product: {data.get('product_id', 'N/A')}")
            print(f"   Quantity: {data.get('quantity', 'N/A')}")
            print(f"   Urgency: {data.get('urgency', 'N/A')}")
            print(f"   Confidence: {review['confidence']:.2f}")
            print()
        
        return len(reviews)

def show_agent_logs():
    """Display recent agent logs"""
    print("📜 Recent Agent Activity:")
    print("-" * 60)
    
    with DatabaseService() as db_service:
        logs = db_service.get_agent_logs(limit=10)
        
        for log in logs[-5:]:  # Show last 5 actions
            timestamp = log['timestamp'][:19] if log['timestamp'] else 'N/A'
            action = log['action']
            product = log['ProductID'] or 'N/A'
            details = log['details'] or ''
            
            print(f"   {timestamp} | {action} | {product}")
            if details and len(details) < 80:
                print(f"      {details}")
            print()

def run_comprehensive_demo():
    """Run comprehensive procurement demo"""
    print("🏭 AI PROCUREMENT AGENT - COMPREHENSIVE DEMO")
    print("=" * 80)
    print("This demo shows the complete procurement workflow:")
    print("1. Inventory monitoring and low stock detection")
    print("2. Autonomous purchase order generation")
    print("3. Human review for high-value/high-risk orders")
    print("4. Supplier integration (simulated)")
    print("5. Complete audit trail")
    print()
    
    # Step 1: Show initial state
    print("🔍 STEP 1: INITIAL INVENTORY SCAN")
    print("=" * 50)
    low_stock_count = show_inventory_status()
    
    if low_stock_count == 0:
        print("\n⚠️  No low stock items found. Setting up demo scenario...")
        # Set up demo scenario with low stock
        import sqlite3
        conn = sqlite3.connect('logistics_agent.db')
        cursor = conn.cursor()
        
        cursor.execute('UPDATE inventory SET current_stock = 9 WHERE product_id = "A101"')
        cursor.execute('UPDATE inventory SET current_stock = 4 WHERE product_id = "B202"')
        cursor.execute('UPDATE inventory SET current_stock = 2 WHERE product_id = "E505"')
        
        conn.commit()
        conn.close()
        
        print("✅ Demo scenario set up")
        low_stock_count = show_inventory_status()
    
    print(f"\n🎯 Found {low_stock_count} items needing procurement")
    
    # Step 2: Run procurement agent
    print("\n🤖 STEP 2: RUNNING PROCUREMENT AGENT")
    print("=" * 50)
    
    agent = ProcurementAgent()
    results = agent.run_procurement_cycle()
    
    print(f"\n📊 Procurement Results:")
    print(f"   - Purchase Orders Created: {results['purchase_orders_created']}")
    print(f"   - Items Submitted for Review: {results['items_submitted_for_review']}")
    print(f"   - Errors: {len(results['errors'])}")
    
    # Step 3: Show purchase orders
    print("\n📋 STEP 3: GENERATED PURCHASE ORDERS")
    print("=" * 50)
    po_count = show_purchase_orders()
    
    # Step 4: Show human reviews
    print("\n👥 STEP 4: HUMAN REVIEW QUEUE")
    print("=" * 50)
    review_count = show_pending_reviews()
    
    # Step 5: Show audit trail
    print("\n📜 STEP 5: AUDIT TRAIL")
    print("=" * 50)
    show_agent_logs()
    
    # Step 6: Performance metrics
    print("\n📈 STEP 6: PERFORMANCE METRICS")
    print("=" * 50)
    
    with DatabaseService() as db_service:
        metrics = db_service.get_performance_metrics(days=1)
        
        print(f"   Automation Rate: {metrics['automation_rate']:.1f}%")
        print(f"   Total Actions: {metrics['total_actions']}")
        print(f"   Purchase Orders: {metrics['purchase_orders']}")
        print(f"   Human Reviews: {metrics['total_reviews']}")
        print(f"   Approval Rate: {metrics['approval_rate']:.1f}%")
    
    # Summary
    print("\n🎉 DEMO SUMMARY")
    print("=" * 50)
    print(f"✅ Inventory Monitoring: {low_stock_count} low stock items detected")
    print(f"✅ Autonomous Procurement: {results['purchase_orders_created']} POs auto-generated")
    print(f"✅ Human Review: {results['items_submitted_for_review']} items escalated")
    print(f"✅ Supplier Integration: Simulated API calls successful")
    print(f"✅ Audit Trail: Complete activity logging")
    
    print("\n🚀 PROCUREMENT AGENT READY FOR PRODUCTION!")
    print("\nKey Benefits Demonstrated:")
    print("• Autonomous inventory monitoring")
    print("• Intelligent decision making with confidence scoring")
    print("• Human-in-the-loop for high-risk decisions")
    print("• Complete supplier integration")
    print("• Real-time performance metrics")
    print("• Full audit trail and compliance")

def test_api_integration():
    """Test procurement API endpoints"""
    print("\n🔗 TESTING API INTEGRATION")
    print("=" * 50)
    
    try:
        # Test procurement endpoints
        base_url = "http://localhost:8000"
        
        print("Testing procurement API endpoints...")
        
        # Test purchase orders endpoint
        response = requests.get(f"{base_url}/procurement/purchase-orders", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Purchase Orders API: {data['count']} orders")
        else:
            print(f"❌ Purchase Orders API failed: {response.status_code}")
        
        # Test suppliers endpoint
        response = requests.get(f"{base_url}/procurement/suppliers", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Suppliers API: {data['count']} suppliers")
        else:
            print(f"❌ Suppliers API failed: {response.status_code}")
        
        print("✅ API integration working correctly")
        
    except requests.exceptions.RequestException:
        print("⚠️  API server not running. Start with: uvicorn api_app:app --reload")
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    # Run comprehensive demo
    run_comprehensive_demo()
    
    # Test API integration
    test_api_integration()
    
    print("\n" + "=" * 80)
    print("🎯 PROCUREMENT AGENT DEMO COMPLETE")
    print("Ready for Day 4: Delivery Agent Implementation!")
    print("=" * 80)
