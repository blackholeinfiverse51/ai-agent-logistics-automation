import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# === Step 2: Load Excel Files ===
orders_df = pd.read_excel("data/orders.xlsx")
restocks_df = pd.read_excel("data/restock_requests.xlsx")

# Convert to dictionary format for GPT
order_data = orders_df.to_dict(orient="records")
restock_data = restocks_df.to_dict(orient="records")

# === Step 3: Create System Prompt ===
system_prompt = f"""
You are a helpful logistics assistant.

Here is the current order data:
{order_data}

Here is the restock data:
{restock_data}

If a user asks:
- "Where is my order #123?" → Search order_data by OrderID and reply with status.
- "When will Product A101 be restocked?" → Search restock_data and reply with quantity.

If the order or product is not found, politely say so.
"""

# === Step 4: Send Message to OpenAI ===
def ask_gpt(user_message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# === Step 5: Chat Loop ===
def run_smart_chat():
    """Run the interactive smart chat loop"""
    print("🤖 Smart Chatbot is running! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        answer = ask_gpt(user_input)
        print("Bot:", answer)

if __name__ == "__main__":
    run_smart_chat()
