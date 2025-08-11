
import json

DATA_PATH = "data/transactions.json"

def sum_amounts_by_filter(start_date=None, end_date=None, category=None, txn_type=None):
    with open(DATA_PATH, "r") as f:
        txns = json.load(f)

    total = 0.0
    for txn in txns:
        if start_date and txn["date"] < start_date:
            continue
        if end_date and txn["date"] > end_date:
            continue
        if category and txn["category"].lower() != category.lower():
            continue
        if txn_type and txn["type"].lower() != txn_type.lower():
            continue
        total += txn["amount"]

    return round(total, 2)
