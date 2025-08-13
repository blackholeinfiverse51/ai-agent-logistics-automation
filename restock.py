import pandas as pd

returns_df = pd.read_excel("data/returns.xlsx")
RESTOCK_THRESHOLD = 5
restock_requests = []

for index, row in returns_df.iterrows():
    product_id = row["ProductID"]
    return_qty = row["ReturnQuantity"]

    if return_qty > RESTOCK_THRESHOLD:
        print(f"Restock needed for Product {product_id}")
        restock_requests.append({
            "ProductID": product_id,
            "RestockQuantity": return_qty
        })

if restock_requests:
    restock_df = pd.DataFrame(restock_requests)
    restock_df.to_excel("data/restock_requests.xlsx", index=False)
    print("✅ Restock requests saved.")
else:
    print("No restock needed.")
