# scripts/generate_dataset.py
import json
import random
from datetime import datetime, timedelta

merchants = ["Amazon", "Costco", "Walmart", "Starbucks", "Delta Airlines",
             "Uber", "Apple", "Best Buy", "Southwest Airlines", "Shell",
             "Netflix", "Home Depot", "Marriott", "Subway", "Target"]

categories = ["Groceries", "Travel", "Dining", "Utilities", "Electronics",
              "Entertainment", "Fuel", "Loan Payment", "Interest Charges"]

types = ["PURCHASE", "PAYMENT", "INTEREST", "INSTALLMENT"]

start_date = datetime(2023, 1, 1)
records = []

for i in range(200):
    txn_date = start_date + timedelta(days=random.randint(0, 780))
    merchant = random.choice(merchants)
    category = random.choice(categories)
    txn_type = random.choice(types)
    amount = round(random.uniform(2, 4500), 2)

    # Lower amounts for coffee/dining, higher for travel/electronics
    if category in ["Dining", "Fuel"]:
        amount = round(random.uniform(2, 50), 2)
    elif category in ["Travel", "Electronics"]:
        amount = round(random.uniform(100, 4500), 2)

    record = {
        "id": f"T{i+1:04}",
        "date": txn_date.strftime("%Y-%m-%d"),
        "merchant": merchant,
        "category": category,
        "type": txn_type,
        "amount": amount
    }
    records.append(record)

with open("data/transactions.json", "w") as f:
    json.dump(records, f, indent=2)

print("Generated data/transactions.json with 200 records.")