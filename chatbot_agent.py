import pandas as pd
import re
from human_review import review_system

# Load Excel files
orders_df = pd.read_excel("data/orders.xlsx")
restocks_df = pd.read_excel("data/restock_requests.xlsx")

# Extract order ID from message
def extract_order_id(message):
    match = re.search(r"#?(\d+)", message)
    if match:
        return int(match.group(1))
    return None

# Extract product ID from message
def extract_product_id(message):
    match = re.search(r"product\s([A-Za-z0-9]+)", message.lower())
    if match:
        return match.group(1).upper()
    return None

# Main chatbot function
def chatbot_response(message):
    original_message = message
    message = message.lower()

    # Check if this query needs human review
    query_data = {"query": original_message}

    if review_system.requires_human_review("chatbot_response", query_data):
        # Submit complex queries for human review
        review_id = review_system.submit_for_review(
            "chatbot_response",
            query_data,
            "Handle complex customer query"
        )
        return f"🔄 Your query has been forwarded to our support team for personalized assistance. Reference ID: {review_id}"

    if "where is my order" in message:
        order_id = extract_order_id(message)
        if order_id is None:
            return "Please provide a valid order number (e.g. #123)."
        order_row = orders_df[orders_df["OrderID"] == order_id]
        if not order_row.empty:
            status = order_row.iloc[0]["Status"]
            return f"📦 Your order #{order_id} is: {status}."
        else:
            return f"❌ I couldn't find order #{order_id}."

    elif "when will product" in message and "restocked" in message:
        product_id = extract_product_id(message)
        if product_id is None:
            return "Please provide a valid product ID (e.g. Product A101)."
        match = restocks_df[restocks_df["ProductID"] == product_id]
        if not match.empty:
            qty = match.iloc[0]["RestockQuantity"]
            return f"🔁 Product {product_id} is pending restock (Qty: {qty})."
        else:
            return f"❌ No restock scheduled for Product {product_id}."

    else:
        return "🤖 I can help with:\n- 'Where is my order #123?'\n- 'When will Product A be restocked?'"

# Chat loop (only run when script is executed directly)
def run_chat():
    """Run the interactive chat loop"""
    print("🤖 Chatbot is running! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print("Bot:", chatbot_response(user_input))

if __name__ == "__main__":
    run_chat()
