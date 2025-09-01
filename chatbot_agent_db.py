#!/usr/bin/env python3
"""
Database-backed chatbot agent for order queries and customer support
"""

import re
from database.service import DatabaseService
from agent_db import DatabaseHumanReviewSystem

# Initialize review system
review_system = DatabaseHumanReviewSystem()

def extract_order_id(message):
    """Extract order ID from message"""
    match = re.search(r"order\s*#?(\d+)", message.lower())
    if match:
        return int(match.group(1))
    return None

def extract_product_id(message):
    """Extract product ID from message"""
    # Look for product followed by alphanumeric ID (like A101, B202)
    match = re.search(r"product\s+([A-Z]\d+)", message.upper())
    if match:
        return match.group(1)
    return None

def extract_tracking_number(message):
    """Extract tracking number from message"""
    # Look for tracking number patterns
    patterns = [
        r"tracking\s*#?\s*([A-Z]{2}\d{9})",  # CO123456789
        r"track\s*#?\s*([A-Z]{2}\d{9})",
        r"([A-Z]{2}\d{9})",  # Direct tracking number
        r"tracking\s*#?\s*([A-Z]+\d+)",  # General pattern
    ]

    for pattern in patterns:
        match = re.search(pattern, message.upper())
        if match:
            return match.group(1)
    return None

def chatbot_response(message):
    """
    Generate chatbot response using database
    """
    message = message.strip()
    
    # Check if human review is needed for this query
    if review_system.requires_human_review("chatbot_response", {"query": message}):
        review_id = review_system.submit_for_review(
            "chatbot_response",
            {"query": message},
            f"Handle customer query: {message[:100]}..."
        )
        return f"🔄 Your query has been forwarded to our support team for personalized assistance. Reference ID: {review_id}"
    
    # Handle order status queries
    if "order" in message.lower() and any(word in message.lower() for word in ["where", "status", "track", "check"]):
        order_id = extract_order_id(message)
        if order_id:
            with DatabaseService() as db_service:
                order = db_service.get_order_by_id(order_id)
                if order:
                    status = order['Status']

                    # Check for shipment information
                    shipment = db_service.get_shipment_by_order(order_id)
                    if shipment:
                        tracking = shipment['tracking_number']
                        shipment_status = shipment['status']
                        estimated = shipment.get('estimated_delivery', 'N/A')

                        return f"📦 Order #{order_id}: {status}\n🚚 Shipment: {shipment_status}\n📍 Tracking: {tracking}\n📅 Est. Delivery: {estimated[:10] if estimated != 'N/A' else 'N/A'}"
                    else:
                        return f"📦 Your order #{order_id} is: {status}."
                else:
                    return f"❌ I couldn't find order #{order_id}. Please check the order number."
        else:
            return "Please provide a valid order number (e.g., 'Where is my order #123?')."

    # Handle delivery/tracking queries
    elif any(word in message.lower() for word in ["delivery", "tracking", "track", "shipment"]):
        # Check for tracking number
        tracking_number = extract_tracking_number(message)
        if tracking_number:
            with DatabaseService() as db_service:
                shipment = db_service.get_shipment_by_tracking(tracking_number)
                if shipment:
                    status = shipment['status']
                    order_id = shipment['order_id']
                    estimated = shipment.get('estimated_delivery', 'N/A')
                    actual = shipment.get('actual_delivery', None)

                    if actual:
                        return f"📦 Tracking {tracking_number}:\n✅ Status: DELIVERED\n📅 Delivered: {actual[:10]}\n🎯 Order: #{order_id}"
                    else:
                        return f"📦 Tracking {tracking_number}:\n🚚 Status: {status.upper()}\n📅 Est. Delivery: {estimated[:10] if estimated != 'N/A' else 'N/A'}\n🎯 Order: #{order_id}"
                else:
                    return f"❌ Tracking number {tracking_number} not found. Please check the number."

        # Check for order ID in delivery context
        order_id = extract_order_id(message)
        if order_id:
            with DatabaseService() as db_service:
                shipment = db_service.get_shipment_by_order(order_id)
                if shipment:
                    tracking = shipment['tracking_number']
                    status = shipment['status']
                    estimated = shipment.get('estimated_delivery', 'N/A')

                    return f"🚚 Delivery for Order #{order_id}:\n📍 Tracking: {tracking}\n🚚 Status: {status.upper()}\n📅 Est. Delivery: {estimated[:10] if estimated != 'N/A' else 'N/A'}"
                else:
                    return f"📦 Order #{order_id} has not been shipped yet."

        return "Please provide an order number or tracking number (e.g., 'Track CO123456789' or 'Where is my delivery for order #123?')."
    
    # Handle restock queries
    elif "product" in message.lower() and "restock" in message.lower():
        product_id = extract_product_id(message)
        if product_id:
            with DatabaseService() as db_service:
                # Check restock requests
                restock_requests = db_service.get_restock_requests()
                product_restocks = [r for r in restock_requests if r['ProductID'] == product_id]
                
                if product_restocks:
                    latest_restock = product_restocks[0]  # Most recent
                    qty = latest_restock['RestockQuantity']
                    status = latest_restock['Status']
                    return f"📈 Product {product_id} restock: {qty} units ({status})"
                else:
                    # Check inventory
                    inventory = db_service.get_inventory()
                    product_inventory = next((item for item in inventory if item['ProductID'] == product_id), None)
                    
                    if product_inventory:
                        current_stock = product_inventory['CurrentStock']
                        reorder_point = product_inventory['ReorderPoint']
                        
                        if current_stock <= reorder_point:
                            return f"📦 Product {product_id} is low in stock ({current_stock} units). Restock may be triggered soon."
                        else:
                            return f"📦 Product {product_id} is in stock ({current_stock} units available)."
                    else:
                        return f"❌ Product {product_id} not found in our inventory."
        else:
            return "Please provide a valid product ID (e.g., 'When will Product A101 be restocked?')."
    
    # Handle inventory queries
    elif any(word in message.lower() for word in ["stock", "available", "inventory"]):
        product_id = extract_product_id(message)
        if product_id:
            with DatabaseService() as db_service:
                inventory = db_service.get_inventory()
                product_inventory = next((item for item in inventory if item['ProductID'] == product_id), None)
                
                if product_inventory:
                    available = product_inventory['AvailableStock']
                    return f"📦 Product {product_id}: {available} units available"
                else:
                    return f"❌ Product {product_id} not found in inventory"
        else:
            # General stock inquiry
            with DatabaseService() as db_service:
                low_stock = db_service.get_low_stock_items()
                if low_stock:
                    items = [f"{item['ProductID']} ({item['CurrentStock']} units)" for item in low_stock[:3]]
                    return f"⚠️ Low stock items: {', '.join(items)}"
                else:
                    return "✅ All items are adequately stocked"
    
    # Handle general help
    elif any(word in message.lower() for word in ["help", "what", "how"]):
        return """🤖 I can help with:
- Order tracking: 'Where is my order #123?'
- Product restocking: 'When will Product A101 be restocked?'
- Stock levels: 'Is Product B202 in stock?'
- General inventory: 'What items are low in stock?'

For complex issues, I'll connect you with our support team."""
    
    # Default response for unrecognized queries
    else:
        return """🤖 I can help with:
- 'Where is my order #123?'
- 'When will Product A101 be restocked?'
- 'Is Product B202 in stock?'

For other questions, please contact our support team."""

def run_chatbot_demo():
    """Run interactive chatbot demo"""
    print("🤖 Database-Backed AI Chatbot")
    print("=" * 40)
    print("Ask me about orders, restocks, or inventory!")
    print("Type 'quit' to exit")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            response = chatbot_response(user_input)
            print(f"Bot: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def test_chatbot():
    """Test chatbot with sample queries"""
    print("🧪 Testing Database-Backed Chatbot")
    print("=" * 40)
    
    test_queries = [
        "Where is my order #101?",
        "What's the status of order 102?",
        "Track CO100000000",
        "Where is my delivery for order #103?",
        "When will product A101 be restocked?",
        "Is product B202 in stock?",
        "What items are low in stock?",
        "Track my shipment CO100000001",
        "This is urgent! My order is wrong!",
        "Help me with my account",
        "Random question"
    ]
    
    for query in test_queries:
        print(f"User: {query}")
        response = chatbot_response(query)
        print(f"Bot:  {response}")
        print("-" * 40)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_chatbot()
    else:
        run_chatbot_demo()
