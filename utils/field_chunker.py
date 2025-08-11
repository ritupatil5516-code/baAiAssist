# utils/field_chunker.py
"""
Field-aware chunking for banking transactions.
Gives more weight to important fields (merchant, category, amount).
"""

def transaction_to_text(txn: dict) -> str:
    """
    Convert a transaction dictionary into a field-weighted text chunk.
    This ensures embeddings capture the most relevant details.
    """
    merchant = txn.get("merchant", "")
    category = txn.get("category", "")
    amount = txn.get("amount", "")
    txn_type = txn.get("type", "")
    date = txn.get("date", "")
    notes = txn.get("notes", "")

    # Weight important fields by repetition
    return (
        f"Transaction {txn.get('id', '')}. "
        f"Date: {date}. "
        f"Merchant: {merchant}. Merchant: {merchant}. "  # Weighted
        f"Category: {category}. Category: {category}. "  # Weighted
        f"Type: {txn_type}. "
        f"Amount: {amount} USD. Amount: {amount} USD. "  # Weighted
        f"Notes: {notes}."
    )