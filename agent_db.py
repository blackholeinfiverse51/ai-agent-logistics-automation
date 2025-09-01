#!/usr/bin/env python3
"""
Database-backed AI Agent for Logistics Automation
Enhanced version with SQLite database instead of Excel files
"""

import pandas as pd
from datetime import datetime
from database.service import DatabaseService
from database.models import init_database
from human_review import HumanReviewSystem

# Configuration
THRESHOLD = 5  # Minimum returns to trigger restock

# Initialize database-backed human review system
class DatabaseHumanReviewSystem(HumanReviewSystem):
    """Database-backed human review system"""
    
    def __init__(self):
        # Don't call parent __init__ as we're using database
        self.confidence_threshold = 0.7
    
    def submit_for_review(self, action_type, data, decision_description):
        """Submit for review using database"""
        import uuid
        review_id = f"{action_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        confidence = self.calculate_confidence(action_type, data)
        
        with DatabaseService() as db_service:
            success = db_service.submit_for_review(
                review_id=review_id,
                action_type=action_type,
                data=data,
                decision_description=decision_description,
                confidence=confidence
            )
            
            if success:
                print(f"⚠️  Action submitted for human review (ID: {review_id}, Confidence: {confidence:.2f})")
                return review_id
            else:
                print(f"❌ Failed to submit for review")
                return None
    
    def get_pending_reviews(self):
        """Get pending reviews from database"""
        with DatabaseService() as db_service:
            return db_service.get_pending_reviews()
    
    def approve_decision(self, review_id, notes=None):
        """Approve decision in database"""
        with DatabaseService() as db_service:
            success = db_service.approve_review(review_id, notes)
            if success:
                print(f"✅ Review {review_id} approved")
            return success
    
    def reject_decision(self, review_id, notes=None):
        """Reject decision in database"""
        with DatabaseService() as db_service:
            success = db_service.reject_review(review_id, notes)
            if success:
                print(f"❌ Review {review_id} rejected")
            return success

# Initialize review system
review_system = DatabaseHumanReviewSystem()

def sense():
    """
    SENSE: Read unprocessed returns from database
    Returns: DataFrame with ProductID and ReturnQuantity
    """
    print("👁️  SENSE: Reading returns data from database...")
    
    with DatabaseService() as db_service:
        returns_data = db_service.get_returns(processed=False)
    
    if not returns_data:
        print("📊 No unprocessed returns found")
        return pd.DataFrame(columns=['ProductID', 'ReturnQuantity'])
    
    # Convert to DataFrame and aggregate by ProductID
    df = pd.DataFrame(returns_data)
    aggregated = df.groupby('ProductID')['ReturnQuantity'].sum().reset_index()
    
    print(f"📊 Found {len(aggregated)} products with returns")
    for _, row in aggregated.iterrows():
        print(f"   - {row['ProductID']}: {row['ReturnQuantity']} returns")
    
    return aggregated

def plan(returns_df):
    """
    PLAN: Analyze returns and decide which products need restocking
    Returns: List of restock decisions
    """
    print("🧠 PLAN: Analyzing returns for restock decisions...")
    
    restocks = []
    
    for _, row in returns_df.iterrows():
        product_id = row['ProductID']
        return_qty = row['ReturnQuantity']
        
        if return_qty > THRESHOLD:
            # Calculate confidence based on quantity and historical data
            confidence = calculate_restock_confidence(product_id, return_qty)
            
            restock_decision = {
                'ProductID': product_id,
                'RestockQuantity': return_qty,
                'Confidence': confidence,
                'Reason': f"Returns ({return_qty}) exceed threshold ({THRESHOLD})"
            }
            restocks.append(restock_decision)
            
            print(f"📈 Restock needed: {product_id} (Qty: {return_qty}, Confidence: {confidence:.2f})")
        else:
            print(f"📉 No restock needed: {product_id} (Qty: {return_qty} <= {THRESHOLD})")
    
    print(f"🎯 Plan complete: {len(restocks)} restock decisions")
    return restocks

def calculate_restock_confidence(product_id, quantity):
    """Calculate confidence score for restock decision"""
    base_confidence = 0.8
    
    # Reduce confidence for very high quantities (might be anomaly)
    if quantity > 20:
        base_confidence -= 0.3
    elif quantity > 15:
        base_confidence -= 0.2
    elif quantity > 10:
        base_confidence -= 0.1
    
    # Check inventory levels
    with DatabaseService() as db_service:
        inventory = db_service.get_inventory()
        product_inventory = next((item for item in inventory if item['ProductID'] == product_id), None)
        
        if product_inventory:
            current_stock = product_inventory['CurrentStock']
            reorder_point = product_inventory['ReorderPoint']
            
            # Increase confidence if stock is low
            if current_stock <= reorder_point:
                base_confidence += 0.1
            # Decrease confidence if stock is high
            elif current_stock > reorder_point * 2:
                base_confidence -= 0.1
    
    return max(0.1, min(1.0, base_confidence))

def act(restock_decisions):
    """
    ACT: Execute restock decisions or submit for human review
    """
    print("⚡ ACT: Executing restock decisions...")
    
    if not restock_decisions:
        print("✅ No actions needed")
        return
    
    with DatabaseService() as db_service:
        for decision in restock_decisions:
            product_id = decision['ProductID']
            quantity = decision['RestockQuantity']
            confidence = decision['Confidence']
            
            # Check if human review is needed
            if review_system.requires_human_review("restock", {"product_id": product_id, "quantity": quantity}):
                # Submit for human review
                review_id = review_system.submit_for_review(
                    "restock",
                    {"product_id": product_id, "quantity": quantity},
                    f"Restock {product_id} with {quantity} units (confidence: {confidence:.2f})"
                )
                
                # Log the review submission
                db_service.log_agent_action(
                    action="restock_review_submitted",
                    product_id=product_id,
                    quantity=quantity,
                    confidence=confidence,
                    human_review=True,
                    details=f"Submitted for review: {review_id}"
                )
            else:
                # Auto-execute high confidence decisions
                success = db_service.create_restock_request(product_id, quantity, confidence)
                
                if success:
                    # Mark returns as processed
                    processed_count = db_service.mark_returns_processed(product_id)
                    
                    # Log the action
                    db_service.log_agent_action(
                        action="restock_created",
                        product_id=product_id,
                        quantity=quantity,
                        confidence=confidence,
                        human_review=False,
                        details=f"Auto-created restock request, processed {processed_count} returns"
                    )
                    
                    print(f"✅ Created restock request: {product_id} (Qty: {quantity})")
                else:
                    print(f"❌ Failed to create restock request for {product_id}")

def run_agent():
    """Main agent execution flow with database backend"""
    print("🤖 Starting Database-Backed AI Agent...")
    print("=" * 50)
    
    try:
        # Initialize database if needed
        init_database()
        
        # Execute agent workflow
        returns = sense()
        plan_result = plan(returns)
        act(plan_result)
        
        # Log completion
        with DatabaseService() as db_service:
            db_service.log_agent_action(
                action="agent_run_completed",
                details=f"Processed {len(returns)} return records, created {len(plan_result)} restock decisions"
            )
        
        print("=" * 50)
        print("✅ Agent execution completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Agent error: {e}")
        
        # Log error
        with DatabaseService() as db_service:
            db_service.log_agent_action(
                action="agent_error",
                details=f"Error: {str(e)}",
                human_review=True
            )
        
        return False

def get_agent_status():
    """Get current agent status and metrics"""
    with DatabaseService() as db_service:
        metrics = db_service.get_performance_metrics(days=7)
        pending_reviews = db_service.get_pending_reviews()
        low_stock = db_service.get_low_stock_items()
        
        return {
            'performance_metrics': metrics,
            'pending_reviews': len(pending_reviews),
            'low_stock_items': len(low_stock),
            'status': 'operational'
        }

if __name__ == "__main__":
    # Run the agent
    success = run_agent()
    
    if success:
        # Show status
        status = get_agent_status()
        print(f"\n📊 Agent Status:")
        print(f"   - Performance: {status['performance_metrics']['automation_rate']:.1f}% automated")
        print(f"   - Pending reviews: {status['pending_reviews']}")
        print(f"   - Low stock items: {status['low_stock_items']}")
    
    print("\n🔗 Database-backed agent ready for production use!")
