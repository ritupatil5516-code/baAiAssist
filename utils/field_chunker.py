
def transaction_to_text(txn: dict) -> str:
    merchant = txn.get("merchant", "")
    category = txn.get("category", "")
    amount = txn.get("amount", "")
    txn_type = txn.get("type", "")
    date = txn.get("date", "")
    notes = txn.get("notes", "")

    return (
        f"Transaction {txn.get('id', '')}. "
        f"Date: {date}. "
        f"Merchant: {merchant}. Merchant: {merchant}. "
        f"Category: {category}. Category: {category}. "
        f"Type: {txn_type}. "
        f"Amount: {amount} USD. Amount: {amount} USD. "
        f"Notes: {notes}."
    )
