import pandas as pd
from datetime import datetime
from human_review import review_system

# === Config ===
RETURNS_FILE = "data/returns.xlsx"
RESTOCK_FILE = "data/restock_requests.xlsx"
LOG_FILE = "data/logs.csv"
THRESHOLD = 5

# === Step 1: Sense ===
def sense():
    print("🔍 Reading returns data...")
    return pd.read_excel(RETURNS_FILE)

# === Step 2: Plan ===
def plan(df):
    print("🧠 Planning restock actions...")
    restocks = []
    for index, row in df.iterrows():
        if row["ReturnQuantity"] > THRESHOLD:
            restocks.append({
                "ProductID": row["ProductID"],
                "RestockQuantity": row["ReturnQuantity"]
            })
    return restocks

# === Step 3: Act ===
def act(restocks):
    if restocks:
        # Check each restock for human review requirement
        approved_restocks = []

        for restock in restocks:
            action_data = {
                "product_id": restock["ProductID"],
                "quantity": restock["RestockQuantity"]
            }

            if review_system.requires_human_review("restock", action_data):
                # Submit for human review
                decision = f"Restock {restock['ProductID']} with quantity {restock['RestockQuantity']}"
                review_id = review_system.submit_for_review("restock", action_data, decision)
                print(f"⏳ Restock for {restock['ProductID']} pending human review (ID: {review_id})")
            else:
                # Auto-approve high confidence decisions
                approved_restocks.append(restock)
                print(f"✅ Auto-approved restock for {restock['ProductID']}")

        # Execute approved restocks
        if approved_restocks:
            print("📝 Writing approved restock requests...")
            df = pd.DataFrame(approved_restocks)
            df.to_excel(RESTOCK_FILE, index=False)
            log_actions(approved_restocks)

        if len(approved_restocks) < len(restocks):
            print(f"ℹ️ {len(restocks) - len(approved_restocks)} restock(s) pending human review")
    else:
        print("ℹ️ No restock needed.")

# === Log actions ===
def log_actions(restocks):
    timestamp = datetime.now().isoformat()
    logs = []
    for item in restocks:
        logs.append({
            "Time": timestamp,
            "Action": "RestockRequest",
            "ProductID": item["ProductID"],
            "Quantity": item["RestockQuantity"]
        })
    df = pd.DataFrame(logs)
    df.to_csv(LOG_FILE, mode='a', index=False, header=not pd.io.common.file_exists(LOG_FILE))
    print("📜 Actions logged.")

# === Main Agent Flow ===
def run_agent():
    returns = sense()
    plan_result = plan(returns)
    act(plan_result)

# === Run ===
if __name__ == "__main__":
    run_agent()
