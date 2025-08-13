#!/usr/bin/env python3
"""
AI Agent Demo Script
Demonstrates the complete logistics automation system
"""

import pandas as pd
import time
import os
from datetime import datetime

# Import our modules
import agent
import chatbot_agent
from human_review import review_system

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🤖 {title}")
    print("="*60)

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n📍 Step {step_num}: {description}")
    print("-" * 40)

def demo_data_overview():
    """Show current data state"""
    print_header("CURRENT DATA OVERVIEW")
    
    try:
        # Show returns data
        returns_df = pd.read_excel("data/returns.xlsx")
        print("📊 Returns Data:")
        print(returns_df.to_string(index=False))
        
        # Show orders data
        orders_df = pd.read_excel("data/orders.xlsx")
        print("\n📦 Orders Data:")
        print(orders_df.to_string(index=False))
        
        # Show existing restock requests
        if os.path.exists("data/restock_requests.xlsx"):
            restock_df = pd.read_excel("data/restock_requests.xlsx")
            print("\n🔄 Existing Restock Requests:")
            print(restock_df.to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error reading data: {e}")

def demo_agent_workflow():
    """Demonstrate the main agent workflow"""
    print_header("AI AGENT WORKFLOW DEMO")
    
    print_step(1, "Agent Sensing (Reading Returns Data)")
    returns_data = agent.sense()
    print(f"✅ Found {len(returns_data)} return records")
    print(returns_data.to_string(index=False))
    
    print_step(2, "Agent Planning (Analyzing Restock Needs)")
    restock_plan = agent.plan(returns_data)
    print(f"✅ Identified {len(restock_plan)} products needing restock:")
    for item in restock_plan:
        print(f"   • {item['ProductID']}: {item['RestockQuantity']} units")
    
    print_step(3, "Agent Acting (Creating Restock Requests)")
    if restock_plan:
        print("🔄 Processing restock decisions...")
        agent.act(restock_plan)
        print("✅ Restock processing complete!")
    else:
        print("ℹ️ No restocks needed at this time")

def demo_chatbot():
    """Demonstrate chatbot capabilities"""
    print_header("CHATBOT DEMO")
    
    test_queries = [
        "Where is my order #101?",
        "Where is my order #102?", 
        "When will product A101 be restocked?",
        "This is urgent! My order is missing!",
        "Help me with something"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print_step(i, f"Query: '{query}'")
        response = chatbot_agent.chatbot_response(query)
        print(f"🤖 Bot Response: {response}")
        time.sleep(1)  # Pause for readability

def demo_human_review():
    """Demonstrate human review system"""
    print_header("HUMAN REVIEW SYSTEM DEMO")
    
    print_step(1, "Checking Pending Reviews")
    pending = review_system.get_pending_reviews()
    
    if pending:
        print(f"⚠️ Found {len(pending)} pending review(s):")
        for review in pending:
            print(f"   • ID: {review['review_id']}")
            print(f"     Type: {review['action_type']}")
            print(f"     Confidence: {review['confidence']:.2f}")
            print(f"     Decision: {review['agent_decision']}")
    else:
        print("✅ No pending reviews")
    
    print_step(2, "Simulating High-Risk Decision")
    # Create a high-risk scenario
    high_risk_data = {
        "product_id": "X999",
        "quantity": 50  # Very high quantity
    }
    
    confidence = review_system.calculate_confidence("restock", high_risk_data)
    print(f"📊 Confidence for 50-unit restock: {confidence:.2f}")
    
    if review_system.requires_human_review("restock", high_risk_data):
        review_id = review_system.submit_for_review(
            "restock", 
            high_risk_data, 
            "Restock X999 with 50 units"
        )
        print(f"⚠️ Decision submitted for review: {review_id}")
    else:
        print("✅ Decision would be auto-approved")

def demo_performance_metrics():
    """Show performance metrics"""
    print_header("PERFORMANCE METRICS")
    
    # Check logs
    if os.path.exists("data/logs.csv"):
        logs_df = pd.read_csv("data/logs.csv")
        print(f"📈 Total agent actions logged: {len(logs_df)}")
        print("Recent actions:")
        print(logs_df.tail().to_string(index=False))
    
    # Check review logs
    if os.path.exists("data/review_log.csv"):
        review_logs_df = pd.read_csv("data/review_log.csv")
        print(f"\n📊 Total human reviews: {len(review_logs_df)}")
        if len(review_logs_df) > 0:
            approved = len(review_logs_df[review_logs_df['human_decision'] == 'approved'])
            approval_rate = (approved / len(review_logs_df)) * 100
            print(f"✅ Approval rate: {approval_rate:.1f}%")
    
    # System health check
    print(f"\n🏥 System Health Check:")
    print(f"   • Data files accessible: {'✅' if os.path.exists('data/orders.xlsx') else '❌'}")
    print(f"   • Agent executable: {'✅' if callable(agent.run_agent) else '❌'}")
    print(f"   • Chatbot responsive: {'✅' if callable(chatbot_agent.chatbot_response) else '❌'}")
    print(f"   • Review system active: {'✅' if callable(review_system.get_pending_reviews) else '❌'}")

def interactive_demo():
    """Run interactive demo"""
    print_header("INTERACTIVE AI AGENT DEMO")
    print("This demo will showcase the complete logistics automation system")
    
    while True:
        print("\n🎯 Demo Options:")
        print("1. Show current data overview")
        print("2. Run agent workflow")
        print("3. Test chatbot")
        print("4. Check human review system")
        print("5. Show performance metrics")
        print("6. Run complete demo")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == "1":
            demo_data_overview()
        elif choice == "2":
            demo_agent_workflow()
        elif choice == "3":
            demo_chatbot()
        elif choice == "4":
            demo_human_review()
        elif choice == "5":
            demo_performance_metrics()
        elif choice == "6":
            # Run complete demo
            demo_data_overview()
            demo_agent_workflow()
            demo_chatbot()
            demo_human_review()
            demo_performance_metrics()
        elif choice == "7":
            print("👋 Demo completed. Thank you!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    try:
        interactive_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Please check your data files and try again.")
